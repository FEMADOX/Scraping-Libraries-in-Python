(() => {
    const oldAddEventListener = EventTarget.prototype.addEventListener;
    window._eventListeners = [];

    EventTarget.prototype.addEventListener = function(type, listener, options) {
        // We describe the element by tag and generally its id or class
        let elemDesc = this.tagName || 'WINDOW/DOC';
        if (this.id) elemDesc += '#' + this.id;
        if (this.className && typeof this.className === 'string') elemDesc += '.' + this.className.split(' ').join('.');

        window._eventListeners.push({
            element: elemDesc,
            type: type,
            listener: listener.toString()
        });

        // Call the original function so the site continues to work
        oldAddEventListener.call(this, type, listener, options);
    };
})()