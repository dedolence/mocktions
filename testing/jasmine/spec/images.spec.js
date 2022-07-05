describe("FileSource.collectImages()", () => {
    const fileSource = new FileSource();
    let mockFile1, mockFile2, mockFile3, urlInputElement, serverResponse;

    beforeEach(function() {
        // create some dummy files to use
        mockFile1 = new File([], 'mockFile1.jpg', {type: 'image/jpg'});
        mockFile2 = new File([], 'mockFile2.jpg', {type: 'image/jpg'});
        mockFile3 = new File([], 'mockFile3.jpg', {type: 'image/jpg'});

        // create a dummy URL input element to simulate user entering a URL of an image
        urlInputElement = document.createElement("input");
        urlInputElement.id = "id_image_url";
        urlInputElement.type = "text";
        urlInputElement.value = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzID6RT9EwTVSFvNuTwh1vLSkKmUE4X_uDhA&usqp=CAU";
        document.body.appendChild(urlInputElement);

        // create a dummy server response to avoid a real fetch request
        responseBody = JSON.stringify({data: {}, image_url: 'imageURL'});
        responseOptions = {headers: {'content-type': 'image/jpeg'}};
        serverResponse = new Response(responseBody, responseOptions);
        spyOn(window, 'makeFetch').and.resolveTo(serverResponse);

        // return a fake presigned URL packet 
        spyOn(fileSource, "getPresignedURLPacket").and.resolveTo({
                file: 'file object',
                data: {key: 'value'},
                url: 'url'
            });

        spyOn(fileSource, "uploadFileToS3").and.resolveTo(
            "https://moctions-static.s3.whatever/path-to-image.jpg"
        );
    });

    it("should add an image (retrieved from supplied URL or a random image) to sourceFileArray if no files are provided", async () => {
        let sourceFiles = await fileSource.collectImages();
        expect(sourceFiles[0]).toEqual(jasmine.any(File));
    });

    it("if no files are given by user but a URL is, use that to retrieve the image", async () => {
        let sourceFiles = await fileSource.collectImages();
        expect(fileSource.sourceURL).toEqual(urlInputElement.value);
    });
});

describe("FileSource.getImageFromURL()", () => {
    const fileSource = new FileSource();
    
    let serverResponse, responseBody, responseOptions;
    let resolvedCheck, rejectedCheck;

    beforeEach(function() {
        responseBody = new File([], "fakeImage", {});
        responseOptions = {'headers': {'content-type': 'image/jpg'}};
        serverResponse = new Request(responseBody, responseOptions);
    });

    it("should return an image if provided a URL", () => {

    });

    it("should return a random image if no URL is provided", () => {

    });

    it("should reject any file that has the wrong content-type", () => {
        resolvedCheck = rejectedCheck = false;
        responseOptions = {'headers': {'content-type': 'applicatin/json'}};
        serverResponse = new Request(responseBody, responseOptions);
        spyOn(window, "makeFetch").and.resolveTo(serverResponse);
        return fileSource.getImageFromURL("fake.url").then((response) => {
            resolvedCheck = true;
        })
        .catch((error) => {
            rejectedCheck = true;
            expect(resolvedCheck).toBe(false);
            expect(rejectedCheck).toBe(true);
        });
    });
});