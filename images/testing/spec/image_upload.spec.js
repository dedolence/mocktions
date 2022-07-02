describe("Collecting files to upload", () => {
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


describe("Processing files for uploading", () => {
    const fileSource = new FileSource();
    let mockFile, uploadedImageURL, fakePacket, mockFileArray;
    let responseBody, responseOptions, serverResponse;

    beforeAll(function() {
    });

    beforeEach(function() {
        // fake files to fake-upload to fake-S3. fake.
        mockFile = new File([], 'mockFile1.jpg', {type: 'image/jpg'});
        mockFileArray = [
            new File([], 'mockFile1.jpg', {type: 'image/jpg'}),
            new File([], 'mockFile2.jpg', {type: 'image/jpg'}),
            new File([], 'mockFile3.jpg', {type: 'image/jpg'})
        ];

        uploadedImageURL = "https://path.to.image.jpg";
        spyOn(fileSource, "uploadFileToS3").and.resolveTo(uploadedImageURL);
        
        // fake S3 presignedURL packet
        fakePacket = {
            file: mockFile,
            data: {
                key1: "value1",
                key2: "value2",
                key3: "value3"
            },
            url: uploadedImageURL
        };
        spyOn(fileSource, "getPresignedURLPacket").and.resolveTo(fakePacket);

        // create a fake response
        const imageURL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzID6RT9EwTVSFvNuTwh1vLSkKmUE4X_uDhA&usqp=CAU";
        responseBody = JSON.stringify({html: '<img src="' + imageURL + '">'});
        responseOptions = {headers: {'content-type': 'application/json'}};
        serverResponse = new Response(responseBody, responseOptions);
        spyOn(window, "makeFetch").and.resolveTo(serverResponse);

        // spy on auxiliary methods generateThumbnail and appendImageURLToForm
        spyOn(fileSource, "generateThumbnail").and.resolveTo(true);
        spyOn(fileSource, "appendImageURLToForm").and.returnValue(true);
    });

    it("should upload a single file", async () => {
        let actualUploadedImageURL = await fileSource.processFile(mockFile);
        expect(actualUploadedImageURL).toEqual(uploadedImageURL);
        expect(fileSource.getPresignedURLPacket).toHaveBeenCalledWith(mockFile);
        expect(fileSource.uploadFileToS3)
            .toHaveBeenCalledWith(
                fakePacket.file, 
                fakePacket.data, 
                fakePacket.url
            );
    });

    it("should upload multiple files concurrently", async () => {
        spyOn(fileSource, "collectImages").and.resolveTo(mockFileArray);
        await fileSource.processAllFiles();
        expect(fileSource.processedImageURLs.length).toEqual(3);
        expect(fileSource.processedImageURLs[0]).toEqual(jasmine.any(String));
        expect(fileSource.getPresignedURLPacket).toHaveBeenCalledTimes(3);
        expect(fileSource.uploadFileToS3).toHaveBeenCalledTimes(3);
    });
});


describe("generating thumbnails and appending images to the DOM", () => {
    const fileSource = new FileSource();
    let imageUrl, thumbnailElement, response, responseBody, responseOptions;
   
    beforeEach(function() {
        // create somewhere to put the thumbnails
        thumbnailElement = document.createElement("div");
        thumbnailElement.id = "id_image_thumbnails";
        document.body.appendChild(thumbnailElement);

        // create a dummy server response
        responseBody = JSON.stringify(
            { html: "<p>Server response HTML</p>" },
        );
        responseOptions = {
            headers: {
                'content-type': 'application/json'
            },
        };
        response = new Response(responseBody, responseOptions);
        
        // a nice picture of a horse
        imageUrl = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzID6RT9EwTVSFvNuTwh1vLSkKmUE4X_uDhA&usqp=CAU";
        
        // return a fake url for ajax requests
        spyOn(window, "getAJAXURL").and.returnValue("some-url");
    });

    afterEach(function() {
        thumbnailElement.remove();
    });

    it("should request formatted HTML from the server", () => { 
        spyOn(window, "makeFetch").and.resolveTo(response);
        return fileSource.generateThumbnail(imageUrl).then(() => {
            expect(window.getAJAXURL).toHaveBeenCalledWith("imageThumbnail");
            expect(window.makeFetch).toHaveBeenCalled();
        });
    });

    it("should append retrieved HTML to the DOM", () => {
        spyOn(window, "makeFetch").and.resolveTo(response);

        // get initial count of thumbnail container's children
        let childCount = thumbnailElement.children.length;

        return fileSource.generateThumbnail(imageUrl).then(() => {
            let currentCount = thumbnailElement.children.length;
            expect(currentCount).toBeGreaterThan(childCount);
        });
    });

    it("should handle a promise rejection in the event of server error", () => {
        spyOn(window, "makeFetch").and.rejectWith(false);
        let resolvedCheck = rejectedCheck = false;
        return fileSource.generateThumbnail(imageUrl).then(() => {
            resolvedCheck = true;
        }).catch((error) => {
            rejectedCheck = true;
            expect(resolvedCheck).toBe(false);
            expect(rejectedCheck).toBe(true);
        });
    });
});


describe("adding and removing uploaded images to/from a form element", () => {
    const fileSource = new FileSource();
    let selectElement, fakeURL1, fakeURL2, fakeURL3;

    beforeEach(function() {
        selectElement = document.createElement("select");
        selectElement.id = "id_image_select";
        document.body.appendChild(selectElement);

        fakeURL1 = "fakeURL1";
        fakeURL2 = "fakeURL2";
        fakeURL3 = "fakeURL3";

    });
    
    afterEach(function() {
        selectElement.remove();
    });

    xit("should append new images to a select element", () => {
        fileSource.appendImageURLToForm()
    });

    xit("should remove a deleted image from select element", () => {

    });
});


describe('Retrieving images from URLs:', () => {
    // this is a LIVE test; i.e. it actually performs the fetch requests. good idea? 
    const fileSource = new FileSource();

    it("should be able to retrieve a specific image from a given URL with specific parameters", () => {
        const imageURL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzID6RT9EwTVSFvNuTwh1vLSkKmUE4X_uDhA&usqp=CAU";
        const imageName = 'horse_picture.jpeg';
        const imageType = 'image/jpeg';
        
        return fileSource.getImageFromURL(imageURL, imageName, imageType)
        .then((image) => {
            expect(image.name).toEqual(imageName);
            expect(image.type).toEqual(imageType);
        });
    });

    it("should reject files that aren't specified as valid MIME types", () => {
        // try getting the minified Bootstrap files why not
        const url = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.min.js";
        const resolvedCheck = rejectedCheck = false;
        return fileSource.getImageFromURL(url, 'filename.zip', 'file/zip')
        .then((res) => {
            resolvedCheck = true;
        })
        .catch((res) => {
            rejectedCheck = true;
            expect(resolvedCheck).toBe(false);
            expect(rejectedCheck).toBe(true);
        });
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
        responseBody = JSON.stringify({data: {}, image_url: 'imageURL'});
        responseOptions = {headers: {'content-type': 'application/json'}};
        serverResponse = new Response(responseBody, responseOptions);
    });

    it("should be able to retrieve a presigned URL for a file to be used for uploading to an S3 bucket", () => {
        // spy on the global makeFetch method and return a fake response
        spyOn(window, 'makeFetch').and.resolveTo(serverResponse);

        return fileSource.getPresignedURLPacket(mockFile).then((packet) => {
            expect(packet.file).toEqual(mockFile);
            expect(packet.data).toEqual(jasmine.any(Object));
            expect(packet.url).toEqual('imageURL');
        });
    });

    it("should handle a promise rejection", () => {
        spyOn(window, 'makeFetch').and.rejectWith("This is the error that should be handled.");
        let resolvedCheck = rejectedCheck = false;
        return fileSource.getPresignedURLPacket(mockFile)
        .then(() => {
            resolvedCheck = true;
        })
        .catch(() => {
            rejectedCheck = true;
            expect(resolvedCheck).toBe(false);
            expect(rejectedCheck).toBe(true);
        });
    });
});


describe("Uploading files to S3", () => {
    const fileSource = new FileSource;
    let file, data, url;

    beforeEach(function() {
        file = new File([], 'mockFile.jpg', {type: 'image/jpg'});
        data = {
            url: "https://path.to.aws.bucket/",
            key1: "value1",
            key2: "value2",
            key3: "value3"
        };
        url = "https://path.to.new.image/image.jpg";
    });

    it("should make a fetch request with the proper parameters", () => {
        // call a dummy fetch request instead of the real one
        spyOn(window, 'makeFetch').and.returnValue(Promise.resolve("Fetch request resolved"));

        return fileSource.uploadFileToS3(file, data, url).then((url) => {
            // determine if makeFetch was called with a FormData object that
            // is the same as the method's data parameter
            let formData = new FormData();
                formData.append('url', data.url);
                formData.append('key1', data.key1);
                formData.append('key2', data.key2);
                formData.append('key3', data.key2);
            expect(window.makeFetch).toHaveBeenCalledWith(data.url, {method: "POST", body: formData});
        });
    });

    it("should handle a fetch request rejection", () => {
        let resolved = rejected = false;
        spyOn(window, 'makeFetch').and.returnValue(Promise.reject("Fetch request rejected!"));
        return fileSource.uploadFileToS3(file, data, url).then(() => {
            resolved = true;
        })
        .catch(() => {
            rejected = true;
            expect(resolved).toBe(false);
            expect(rejected).toBe(true);
        });
    });

    it("should return the URL of the file to be uploaded", () => {
        spyOn(window, 'makeFetch').and.returnValue(Promise.resolve("Fetch request resolved"));

        return fileSource.uploadFileToS3(file, data, url).then((returnedURL) => {
            expect(returnedURL).toEqual(url);
        });
    });
});


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
});
