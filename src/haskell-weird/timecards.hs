-- DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite desechable bajo
-- XDG_DATA_HOME. Nada de esto toca un sistema real de registro de horas.
--
-- Run: runghc timecards.hs
--
-- EL TRUCO: una lista infinita de tarjetas cuyos *elementos tienen efectos secundarios*.
--
-- Forzar la celda n de la lista imprime la tarjeta n y envía su INSERT a
-- sqlite3. Nada más en el programa escribe una fila. Así que la regla de parada no es
-- "un bucle que decide cuándo salir": es un consumidor (@span@) que simplemente
-- deja de pedir la celda siguiente, y los INSERT se detienen con él.
--
-- No hay bucle, ni acumulador, ni recursión, ni contador. Se atan dos nudos
-- con 'fix'/'fixIO':
--
--   * el flujo aleatorio es una lista definida en términos de sí misma;
--   * el total acumulado de cada tarjeta se lee de la tarjeta anterior, que es
--     un elemento de la misma lista que se está construyendo.
--
-- 'unsafeInterleaveIO' hace que una acción de IO espere hasta que se pida su celda.
-- Se llama "unsafe" (insegura) porque entonces el orden de los efectos lo decide
-- el evaluador, no el texto del programa. Aquí eso es justo lo que se busca.
module Main (main) where

import Control.Exception (evaluate)
import Data.Bits (shiftR)
import Data.Function (fix)
import Data.List (intercalate)
import Data.Time (defaultTimeLocale, formatTime, getCurrentTime, getZonedTime)
import Data.Time.Clock.POSIX (utcTimeToPOSIXSeconds)
import Data.Word (Word64)
import System.Directory (XdgDirectory (XdgData), createDirectoryIfMissing, getXdgDirectory)
import System.Exit (ExitCode (ExitSuccess))
import System.FilePath ((</>))
import System.IO (Handle, fixIO, hClose, hPutStrLn)
import System.IO.Unsafe (unsafeInterleaveIO)
import System.Posix.Process (getProcessID)
import System.Process (CreateProcess (std_in), StdStream (CreatePipe), createProcess, proc, waitForProcess)

data Category = Meetings | Coding | Debugging | Learning
  deriving (Show, Enum, Bounded)

data Card = Card
  { category :: Category,
    hours :: Int,
    runningTotal :: Int
  }

-- | Horas de 10 a 19, como una lista definida en términos de sí misma: cada elemento es
-- el paso del generador aplicado al anterior. (Un LCG de 64 bits con las
-- constantes de Knuth; 'Word64' da la vuelta al desbordarse, que es el "mod 2^64".)
rolls :: Word64 -> [Int]
rolls seed = map toHours (tail (fix (\xs -> seed : map next xs)))
  where
    next s = s * 6364136223846793005 + 1442695040888963407
    toHours s = 10 + fromIntegral ((s `shiftR` 33) `mod` 10)

-- | Convierte una lista de acciones de IO en una acción de IO de una lista, pero *de forma perezosa*: el
-- efecto de cada elemento se ejecuta solo cuando se fuerza esa celda del resultado.
-- ('sequence' normal ejecutaría todas las acciones y, con una lista infinita, nunca
-- terminaría.)
lazily :: [IO a] -> IO [a]
lazily = fix $ \self actions ->
  unsafeInterleaveIO $ case actions of
    [] -> pure []
    act : rest -> (:) <$> act <*> self rest

-- | La hoja interminable de tarjetas. @onBirth@ es lo que le pasa a una tarjeta en el momento en que
-- nace; es el único lugar donde hay salida.
--
-- El nudo: @cards@ es el resultado, y @before@ es "0, y luego el total de cada
-- tarjeta" -- así que el total de la tarjeta n se lee de la tarjeta n-1, un elemento de la lista
-- en construcción. 'fixIO' nos entrega esa lista antes de que exista.
sheet :: (Card -> IO ()) -> Word64 -> IO [Card]
sheet onBirth seed = fixIO $ \cards ->
  let before = 0 : map runningTotal cards
      born (c, h, t) = let card = Card c h (t + h) in card <$ onBirth card
   in lazily (map born (zip3 (cycle [minBound ..]) (rolls seed) before))

-- | La regla de parada. No es más que cuánto de la lista elegimos leer:
-- todo hasta el primer total de más de 40, más esa tarjeta.
untilOver40 :: [Card] -> [Card]
untilOver40 cards = under ++ take 1 over
  where
    (under, over) = span ((<= 40) . runningTotal) cards

schema :: String
schema =
  concat
    [ "CREATE TABLE IF NOT EXISTS demo_timecards(",
      "id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,hours INTEGER,",
      "running_total INTEGER,iso_week TEXT,created_at TEXT,",
      "demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));"
    ]

quote :: String -> String
quote s = "'" ++ concatMap (\c -> if c == '\'' then "''" else [c]) s ++ "'"

insert :: String -> String -> Card -> String
insert run week card =
  "INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week,created_at) VALUES("
    ++ intercalate
      ","
      [ quote run,
        quote (show (category card)),
        show (hours card),
        show (runningTotal card),
        quote week,
        "datetime('now')"
      ]
    ++ ");"

row :: String -> Card -> String
row week card =
  intercalate
    "\t"
    [show (category card), show (hours card), show (runningTotal card), week, "DEMO ONLY"]

-- | Lo que le pasa a una tarjeta al nacer: mostrarla y guardarla.
emit :: Handle -> String -> String -> Card -> IO ()
emit sqlite run week card = do
  putStrLn (row week card)
  hPutStrLn sqlite (insert run week card)

main :: IO ()
main = do
  now <- getCurrentTime
  pid <- getProcessID
  week <- formatTime defaultTimeLocale "%G-W%V" <$> getZonedTime
  dir <- getXdgDirectory XdgData "HaskellWeird"
  createDirectoryIfMissing True dir
  (Just sqlite, _, _, process) <-
    createProcess (proc "sqlite3" [dir </> "demo-timecards.db"]) {std_in = CreatePipe}
  let micros = floor (utcTimeToPOSIXSeconds now * 1000000) :: Word64
      run = show (micros `div` 1000000) ++ "-" ++ show pid
  putStrLn ("# DEMO ONLY run " ++ run)
  hPutStrLn sqlite "BEGIN;"
  hPutStrLn sqlite schema
  -- Todavía no se ha escrito nada salvo el esquema: la lista es solo una promesa.
  cards <- untilOver40 <$> sheet (emit sqlite run week) (micros * 7919 + fromIntegral pid)
  -- Contar las tarjetas conservadas es lo que las pide y, por tanto, lo que ejecuta los efectos.
  -- (Prueba aquí un `let entries = length cards` perezoso: el conteo no se pide hasta
  -- que se imprime el resumen, después de COMMIT, y la tubería ya está cerrada.)
  entries <- evaluate (length cards)
  hPutStrLn sqlite "COMMIT;"
  hClose sqlite
  status <- waitForProcess process
  if status == ExitSuccess then pure () else ioError (userError "sqlite3 failed")
  putStrLn ("# committed total=" ++ show (sum (map hours cards)) ++ " entries=" ++ show entries ++ " DEMO ONLY")
  putStrLn "# the list of cards is a fixed point of itself, and reading it is what wrote the rows"
