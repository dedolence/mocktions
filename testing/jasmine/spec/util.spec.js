describe("$()", () => {
    let element, elementID = "testElement", elementClass = "testClass";

    beforeEach(function() {
        element = document.createElement("div");
        element.id = elementID;
        element.classList.add(elementClass);
        document.body.appendChild(element);
    });

    afterEach(function() {
        element.remove();
    });

    it("should return an HTML element when provided an ID", () => {
        let result = $("#testElement");
        expect(result.id).toEqual(elementID);
        expect(result).toEqual(jasmine.any(HTMLElement));
    });

    it("should default to using an ID as a selector when none is provided", () => {
        let result = $("testElement");
        expect(result.id).toEqual(elementID);
        expect(result).toEqual(jasmine.any(HTMLElement));
    });

    it("should return an instance of a class if provided with a class selector", () => {
        let result = $(".testClass");
        expect(result.id).toEqual(elementID);
        expect(result.classList.contains(elementClass)).toBe(true);
        expect(result).toEqual(jasmine.any(HTMLElement));
    });
});


describe("getAJAXURL()", () => {
    it("should return the correct URL", () => {
        let url1 = getAJAXURL('imageThumbnail');
        let url2 = getAJAXURL('presignedURL');
        let def = getAJAXURL('foobar');
        expect(url1).toBe('ajax/get_image_thumbnail');
        expect(url2).toBe('ajax/get_presigned_URL');
        expect(def).toBe('ajax/default_url');
    });

    it("should append keys/values to a URL if provided", () => {
        let params = {
            key1: 'value1',
            key2: 69,
            key3: 'шеллы'    // test encoding
        }
        let url = getAJAXURL('foobar', params);
        expect(url).toBe('ajax/default_url?key1=value1&key2=69&key3=%D1%88%D0%B5%D0%BB%D0%BB%D1%8B');
    });
});


describe("makeFetch()", () => {
    const options = {
        method: "GET",
    }

    const responseStatustester = {
        asymmetricMatch: function(actual) {
            return actual >= 200 && actual <= 299;
        }
    }

    it("should fetch any arbitrary response from a server", () => {
        const successfulURL = "https://randomuser.me/api/";
        return makeFetch(successfulURL).then((response) => {
            expect(response.status).toEqual(responseStatustester);
        });
    });

    it("should return an error if there was a problem", () => {
        const unsuccessfulURL = "https://doesnt.exist.com";
        let resolvedCheck = rejectedCheck = false;
        return makeFetch(unsuccessfulURL)
        .then((response) => {
            resolvedCheck = true;
        })
        .catch((error) => {
            rejectedCheck = true;
            expect(resolvedCheck).toEqual(false);
            expect(rejectedCheck).toEqual(true);
        });
    });
});