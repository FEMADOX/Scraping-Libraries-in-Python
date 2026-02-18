const callback = arguments[arguments.length - 1]

const autoScroll = async (container = document.scrollingElement) => {
  const pause = 800
  const maxRounds = 500
  let lastHeight = 0

  for (let round = 0; round < maxRounds; round++) {
    container.scrollTo(0, container.scrollHeight)
    await new Promise(response => setTimeout(response, pause))

    const newHeight = container.scrollHeight
    console.log(`Round ${round + 1}: Scrolled to ${newHeight}px`)

    if (newHeight === lastHeight) {
      console.log('No more content to load. Stopping auto-scroll.')
      break
    }
    lastHeight = newHeight
  }
}

const findScrollableAncestor = () => {
  const elements = Array.from(document.querySelectorAll('body *'))

  for (const element of elements) {
    const style = getComputedStyle(element)

    if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && element.scrollHeight > element.clientHeight) return element
  }

  return document.scrollingElement || document.documentElement
}

const container = findScrollableAncestor()

autoScroll(container).then(r => {callback})