() => {
  document.body.addEventListener("click", () => console.log("Body clicked!"))

  document.body.addEventListener("mouseover", () => console.log("Mouse over body!"))

  document.body.addEventListener("scroll", () => console.log("Body scrolled!"))
}