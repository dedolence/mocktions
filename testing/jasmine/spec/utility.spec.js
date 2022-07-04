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