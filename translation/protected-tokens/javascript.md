<!-- GENERATED from tokens.jsonl by tools/token_registry.py; do not edit by hand -->
# Protected tokens: javascript

- Status: extracted
- Version tested: Node v24.15.0
- Extraction command: `node -e <probe script in tools/token_registry.py JS_SCRIPT>`

## Reserved words (36)

`break` `case` `catch` `class` `const` `continue` `debugger` `default` `delete` `do` `else` `enum` `export` `extends` `false` `finally` `for` `function` `if` `import` `in` `instanceof` `new` `null` `return` `super` `switch` `this` `throw` `true` `try` `typeof` `var` `void` `while` `with`

## Contextual words (11)

`arguments` `eval` `implements` `interface` `let` `package` `private` `protected` `public` `static` `yield`

## Standard API names (179)

`AbortController` `AbortSignal` `AggregateError` `Array` `ArrayBuffer` `AsyncDisposableStack` `Atomics` `BigInt` `BigInt64Array` `BigUint64Array` `Blob` `Boolean` `BroadcastChannel` `Buffer` `ByteLengthQueuingStrategy` `CloseEvent` `CompressionStream` `CountQueuingStrategy` `Crypto` `CryptoKey` `CustomEvent` `DOMException` `DataView` `Date` `DecompressionStream` `DisposableStack` `Error` `EvalError` `Event` `EventTarget` `File` `FinalizationRegistry` `Float16Array` `Float32Array` `Float64Array` `FormData` `Function` `Headers` `Infinity` `Int16Array` `Int32Array` `Int8Array` `Intl` `Iterator` `JSON` `Map` `Math` `MessageChannel` `MessageEvent` `MessagePort` `NaN` `Navigator` `Number` `Object` `Performance` `PerformanceEntry` `PerformanceMark` `PerformanceMeasure` `PerformanceObserver` `PerformanceObserverEntryList` `PerformanceResourceTiming` `Promise` `Proxy` `RangeError` `ReadableByteStreamController` `ReadableStream` `ReadableStreamBYOBReader` `ReadableStreamBYOBRequest` `ReadableStreamDefaultController` `ReadableStreamDefaultReader` `ReferenceError` `Reflect` `RegExp` `Request` `Response` `Set` `SharedArrayBuffer` `String` `SubtleCrypto` `SuppressedError` `Symbol` `SyntaxError` `TextDecoder` `TextDecoderStream` `TextEncoder` `TextEncoderStream` `TransformStream` `TransformStreamDefaultController` `TypeError` `URIError` `URL` `URLPattern` `URLSearchParams` `Uint16Array` `Uint32Array` `Uint8Array` `Uint8ClampedArray` `WeakMap` `WeakRef` `WeakSet` `WebAssembly` `WebSocket` `WritableStream` `WritableStreamDefaultController` `WritableStreamDefaultWriter` `assert` `async_hooks` `atob` `btoa` `buffer` `child_process` `clearImmediate` `clearInterval` `clearTimeout` `cluster` `console` `constants` `crypto` `decodeURI` `decodeURIComponent` `dgram` `diagnostics_channel` `dns` `domain` `encodeURI` `encodeURIComponent` `escape` `eval` `events` `exports` `fetch` `fs` `global` `globalThis` `http` `http2` `https` `inspector` `isFinite` `isNaN` `module` `navigator` `net` `node:sea` `node:sqlite` `node:test` `os` `parseFloat` `parseInt` `path` `perf_hooks` `performance` `process` `punycode` `querystring` `queueMicrotask` `readline` `repl` `require` `setImmediate` `setInterval` `setTimeout` `stream` `string_decoder` `structuredClone` `sys` `timers` `tls` `trace_events` `tty` `undefined` `unescape` `url` `util` `v8` `vm` `wasi` `worker_threads` `zlib`

## Positive examples (stay as written)

- `const total = cards.length;`
- `console.log(total);`

## Negative examples (do not compile)

- `var class = 1;`
- `var export = 2;`

## Compile fixtures

47 of 47 passed.
