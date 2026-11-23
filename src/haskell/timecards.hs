-- DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo
-- XDG_DATA_HOME. Nada de esto toca un sistema real de registro de horas.
--
-- Ejecuta: runghc timecards.hs
--
-- El reto ("suma tarjetas de 10 a 19 horas hasta que el total acumulado pase de 40") es
-- la función pura 'timecards'. Todo lo de 'main' es fontanería: pedir al
-- reloj una semilla, ejecutar la función y pasarle la respuesta a sqlite3.
module Main (main) where

import Data.Bits (shiftR)
import Data.List (intercalate)
import Data.Time (defaultTimeLocale, formatTime, getCurrentTime, getZonedTime)
import Data.Time.Clock.POSIX (utcTimeToPOSIXSeconds)
import Data.Word (Word64)
import System.Directory (XdgDirectory (XdgData), createDirectoryIfMissing, getXdgDirectory)
import System.FilePath ((</>))
import System.Posix.Process (getProcessID)
import System.Process (readProcess)

-- ---------------------------------------------------------------------------
-- The challenge
-- ---------------------------------------------------------------------------

data Category = Meetings | Coding | Debugging | Learning
  deriving (Show, Enum, Bounded)

data Card = Card
  { category :: Category,
    hours :: Int,
    runningTotal :: Int
  }

-- | Un flujo infinito y repetible de horas entre 10 y 19.
--
-- GHC no trae ningún paquete de números aleatorios, así que esto es un generador
-- congruencial lineal de 64 bits (constantes MMIX de Knuth). La aritmética de 'Word64' da la vuelta al
-- desbordarse, que es justo el "mod 2^64" que pide el algoritmo. Los bits
-- bajos de un LCG son débiles, así que usamos los altos.
rolls :: Word64 -> [Int]
rolls = map toHours . tail . iterate next
  where
    next s = s * 6364136223846793005 + 1442695040888963407
    toHours s = 10 + fromIntegral ((s `shiftR` 33) `mod` 10)

-- | Todas las tarjetas que podrían existir: las categorías se repiten y cada tarjeta
-- lleva el total hasta ese momento. 'scanl1' es una suma acumulada.
allCards :: Word64 -> [Card]
allCards seed = zipWith3 Card (cycle [minBound ..]) hs (scanl1 (+) hs)
  where
    hs = rolls seed

-- | Sigue sumando tarjetas hasta que el total pase de 40, y conserva la que
-- cruza la línea. La pereza es la razón de que termine: 'span' deja de leer la
-- lista infinita en la primera tarjeta que supera el límite.
timecards :: Word64 -> [Card]
timecards seed = under ++ take 1 over
  where
    (under, over) = span ((<= 40) . runningTotal) (allCards seed)

-- ---------------------------------------------------------------------------
-- Output
-- ---------------------------------------------------------------------------

schema :: String
schema =
  concat
    [ "CREATE TABLE IF NOT EXISTS demo_timecards(",
      "id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,hours INTEGER,",
      "running_total INTEGER,iso_week TEXT,created_at TEXT,",
      "demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));"
    ]

-- | Un literal de cadena SQL. Duplicar las comillas internas es toda la regla de escape;
-- aquí las entradas son fijas, pero una función auxiliar segura igualmente no cuesta nada.
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

-- ---------------------------------------------------------------------------
-- Plumbing
-- ---------------------------------------------------------------------------

main :: IO ()
main = do
  now <- getCurrentTime
  pid <- getProcessID
  week <- formatTime defaultTimeLocale "%G-W%V" <$> getZonedTime
  dir <- getXdgDirectory XdgData "Haskell"
  let micros = floor (utcTimeToPOSIXSeconds now * 1000000) :: Word64
      seed = micros * 7919 + fromIntegral pid
      run = show (micros `div` 1000000) ++ "-" ++ show pid
      cards = timecards seed
      sql = unlines (["BEGIN;", schema] ++ map (insert run week) cards ++ ["COMMIT;"])
  createDirectoryIfMissing True dir
  _ <- readProcess "sqlite3" [dir </> "demo-timecards.db"] sql
  putStr . unlines $
    ["# DEMO ONLY run " ++ run]
      ++ map (row week) cards
      ++ [ "# committed total=" ++ show (sum (map hours cards)) ++ " entries=" ++ show (length cards) ++ " DEMO ONLY",
           "# the whole challenge is one pure function, timecards; main is just plumbing"
         ]
