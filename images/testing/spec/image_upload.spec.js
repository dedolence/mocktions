describe('Retrieving images from URLs:', () => {
    /* 
        asynchronous functions get tested as such:
            return asyncFunction.then(function(any_returned_value) {
                expect()...
            });
    */
    const fileSource = new FileSource();

    const imageTypeTester = {
        asymmetricMatch: function(actual) {
            const acceptedFileTypes = ['image/jpg', 'image/jpeg', 'image/png', 'image/webp', 'image/gif'];
            return acceptedFileTypes.includes(actual);
        }
    }

    it("should have a property called fileArray that is an array", () => {
        expect(fileSource.sourceFileArray).toEqual(jasmine.any(Array));
    });

    it("should be able to retrieve a random image using parameter defaults", () => {
        return fileSource.getImageFromURL().then((image) => {
            expect(image.type).toEqual(imageTypeTester);
            expect(image.name).toEqual('image.jpg');
        })
    });

    it("should be able to retrieve a specific image from a given URL with specific parameters", () => {
        const imageURL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzID6RT9EwTVSFvNuTwh1vLSkKmUE4X_uDhA&usqp=CAU";
        const imageName = 'horse_picture.jpeg';
        const imageType = 'image/jpeg';
        
        return fileSource.getImageFromURL(imageURL, imageName, imageType)
        .then((image) => {
            expect(image.name).toEqual(imageName);
            expect(image.type).toEqual(imageType);
        })
    });
});


describe("Presigned URLS:", () => {
    const fileSource = new FileSource();
    let mockFile, urlElement, serverResponse;

    beforeEach(function() {
        // create a fake file
        mockFile = new File([], 'mockFile.jpg', {type: 'image/jpg'});

        // create the element from which the method will retrieve the path to the server
        urlElement = document.createElement('input');
        urlElement.type = 'hidden';
        urlElement.name='sign_s3_url';
        urlElement.value='ajax_url';
        document.body.appendChild(urlElement);

        // create a fake response
        serverResponse = new Response(JSON.stringify(
            {
                data: {}, 
                image_url: 'imageURL'
            }
        ));

    })

    it("should be able to retrieve a presigned URL for a file to be used for uploading to an S3 bucket", () => {
        // spy on the global makeFetch method and return a fake response
        spyOn(window, 'makeFetch').and.returnValue(Promise.resolve(serverResponse));

        return fileSource.getPresignedURLPacket(mockFile).then((packet) => {
            expect(packet.file).toEqual(mockFile);
            expect(packet.data).toEqual(jasmine.any(Object));
            expect(packet.url).toEqual('imageURL');
        });
    });

    it("should handle a promise rejection", () => {
        spyOn(window, 'makeFetch').and.returnValue(Promise.reject("This is the error that should be handled."));
        let resolvedCheck = rejectedCheck = false;
        return fileSource.getPresignedURLPacket(mockFile)
        .then(() => {
            resolvedCheck = true;
        })
        .catch(() => {
            rejectedCheck = true;
            expect(resolvedCheck).toBe(false);
            expect(rejectedCheck).toBe(true);
        })
    })
})


describe("The makeFetch() function", () => {
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
})

/* 
describe("The makeFetch() function checklist:", () => {
    const realURL = 'https://picsum.photos/300';
    const fakeURL = "https://here.is.a.fake.url";
    const jsonUrl = 'https://randomuser.me/api/';
    const formData = new FormData();
    const fileTypeTester = {
        asymmetricMatch: function(actual) {
            const acceptedFileTypes = ['image/jpg', 'image/png', 'image/webp', 'image/gif'];
            return acceptedFileTypes.includes(actual);
        }
    }
    const options = {
        method: 'GET',
        fileName: 'testFile.jpg',
        fileType: 'image/jpg',
        type: 'file',
    };

    it("should successfully retrieve an image from a real URL", () => {
        return makeFetch(realURL, options).then((file) => {
            expect(file.type).toEqual(fileTypeTester);
        });
    });

    it("should successfully retrieve and parse JSON data", () => {
        options.type = 'json';
        return makeFetch(jsonUrl, options).then((json) => {
            expect(json).toEqual(jasmine.any(Object));
        })
    });

    it("should reject with an error when the URL is incorrect", () => {
        let res = false;
        let rej = false;
        return makeFetch(fakeURL, options)
        .then((res) => {
            // this shouldn't be encountered if the promise rejects
            res = true;
        })
        .catch((err) => {
            rej = true;
            expect(res).toEqual(false);
            expect(rej).toEqual(true);
        });
    });
}); */
