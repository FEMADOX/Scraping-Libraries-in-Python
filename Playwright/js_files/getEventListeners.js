(element => {
  // getEventListeners works only in DevTools
  // The debugger statement is used to trigger the DevTools to open, which allows us to debug the code and access the getEventListeners function.
  // debugger // ! <- Without the Chrome DevTools open, this won't work, so we need to trigger the DevTools to open before using this js file.
  // ⬆️ Uncomment `debugger` to debug the JS code
  if (typeof getEventListeners === "function") {
    const listeners = getEventListeners(element)
    const result = []
    for (const [type, funcs] of Object.entries(listeners)) {
      funcs.forEach(funct => result.push({ type: type, listener: funct.listener.toString() }))
    }
    return result
  }
  return []
})(document.body)