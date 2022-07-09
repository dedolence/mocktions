describe("getAJAXURL()", () => {
    it("should return the correct URL", () => {
        let url1 = getAJAXURL('imageThumbnail');
        let url2 = getAJAXURL('presignedURL');
        let def = getAJAXURL('foobar');
        expect(url1).toBe('ajax/get_image_thumbnail');
        expect(url2).toBe('ajax/get_presigned_URL');
        expect(def).toBe('ajax/default_url');
    });

    xit("should append keys/values to a URL if provided", () => {
        let params = {
            key1: 'value1',
            key2: 69,
            key3: 'Тест'    // test encoding
        }
        let url = getAJAXURL('foobar', params);
        expect(url).toBe('ajax/default_url?key1=value1&key2=69&key3=%D0%A2%D0%B5%D1%81%D1%82');
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