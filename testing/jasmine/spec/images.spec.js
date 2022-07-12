// SETUP: 
// Add a beforeAll() to each suite that calls elementGenerator();
// Add an afterAll() to each suite that calls elementRemover();
// Instantiate FileSource in the beforeEach() method, not before!

/**
 * Add a line for each DOM element that needs to be appended in order
 * for FileSource to be instantiated.
 * @param {object} element 
 * @param {String} element.id ID attribute.
 * @param {String} element.node What type of element to create using document.createElement().
 * @param {String} element.type For input elements, type of input, e.g. text, file, etc..
 */
const elements = [
    {id: 'id_image_select', node: 'select', type: ''},
    {id: 'id_image_url_input', node: 'input', type: 'text'},
    {id: 'id_image_loading_modal', node: 'div', type: ''},
    {id: 'id_file_input', node: 'input', type: 'file'},
    {id: 'id_thumbnail_container', node: 'div', type: ''},
    {id: 'id_process_uploads_trigger', node: 'input', type: 'button'},
];


/**
 * Returns an object of element parameters to their IDs. {id: 'id'}
 */
const ids = Object.fromEntries(elements.map((e) => { return [e.id, e.id] }));

/**
 * Iterates through the elements array and creates/appends each to DOM.
 * @returns {void}
 */
function elementGenerator(caller) {
    return new Promise((res, rej) => {
        for (el of elements) {
            let _ = document.createElement(el.node);
            _.id = el.id;
            if (el.type) {
                _.type = el.type;
            }
            _.classList.add("tempDOMelement");  // for removing later
            document.body.appendChild(_);
        }
        res();
    });
}

/**
 * Removes all elements with class "tempDOMelement" from DOM.
 * @returns {void}
 */
function elementRemover(caller) {
    let nodes = document.querySelectorAll(".tempDOMelement");
    for (let node of nodes) {
        node.remove();
    }
}


describe("FileSource.collectImages()", () => {
    let fileSource, mockFile1, mockFile2, mockFile3, urlInputElement, serverResponse;
    
    beforeAll(function() {
        elementGenerator("collectImages()");
    });

    afterAll(function() {
        elementRemover("collectImages()");
    });

    beforeEach(function() {
        fileSource = new FileSource();

        // create some dummy files to use
        mockFile1 = new File([], 'mockFile1.jpg', {type: 'image/jpg'});
        mockFile2 = new File([], 'mockFile2.jpg', {type: 'image/jpg'});
        mockFile3 = new File([], 'mockFile3.jpg', {type: 'image/jpg'});

        // add an image URL to the input
        urlInputElement = document.getElementById("id_image_url_input");
        urlInputElement.value = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzID6RT9EwTVSFvNuTwh1vLSkKmUE4X_uDhA&usqp=CAU";

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

        // just need a resolved promise that looks like a string
        spyOn(fileSource, "uploadFileToS3").and.resolveTo(
            "https://moctions-static.s3.whatever/path-to-image.jpg"
        );
    });

    it("should add an image (retrieved from supplied URL or a random image) to sourceFileArray if no files are provided", async () => {
        let sourceFiles = await fileSource.collectImages(fileSource.urlInputElement, fileSource.sourceFileElement);
        expect(sourceFiles[0]).toEqual(jasmine.any(File));
    });

    it("if no files are given by user but a URL is, use that to retrieve the image", async () => {
        let sourceFiles = await fileSource.collectImages(fileSource.urlInputElement, fileSource.sourceFileElement);
        expect(fileSource.sourceURL).toEqual(urlInputElement.value);
    });
});


describe("FileSource.constructor", () => {
        
    beforeAll(function() {
        elementGenerator("generateThumbnail()");
    });

    afterAll(function() {
        elementRemover("generateThumbnail()");
    });

    let fileSource;

    beforeEach(function() {
        fileSource = new FileSource();
        spyOn(fileSource, 'processAllFiles');
    });

    xit("should, on instantiating, add a button that triggers uploads", () => {
        fileSource.processTriggerElement.click();
        expect(fileSource.processAllFiles).toHaveBeenCalled();
    });
});


describe("FileSource.generateThumbnail()", () => {
    
    beforeAll(function() {
        elementGenerator("generateThumbnail()");
    });

    afterAll(function() {
        elementRemover("generateThumbnail()");
    });

    let fileSource, imageUrl, thumbnailElement, response, responseBody, responseOptions;
   
    beforeEach(function() {

        fileSource = new FileSource();

        thumbnailElement = document.getElementById('id_thumbnail_container');

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

    it("should request formatted HTML from the server", () => { 
        spyOn(window, "makeFetch").and.resolveTo(response);
        return fileSource.generateThumbnail(imageUrl, thumbnailElement).then(() => {
            expect(window.getAJAXURL).toHaveBeenCalledWith("imageThumbnail", {'imageURL': imageUrl});
            expect(window.makeFetch).toHaveBeenCalled();
        });
    });

    it("should append retrieved HTML to the DOM", () => {
        spyOn(window, "makeFetch").and.resolveTo(response);

        // get initial count of thumbnail container's children
        let childCount = thumbnailElement.children.length;

        return fileSource.generateThumbnail(imageUrl, thumbnailElement).then(() => {
            let currentCount = thumbnailElement.children.length;
            expect(currentCount).toBeGreaterThan(childCount);
        });
    });

    it("should handle a promise rejection in the event of server error", () => {
        spyOn(window, "makeFetch").and.rejectWith(false);
        let resolvedCheck = rejectedCheck = false;
        return fileSource.generateThumbnail(imageUrl, thumbnailElement).then(() => {
            resolvedCheck = true;
        }).catch((error) => {
            rejectedCheck = true;
            expect(resolvedCheck).toBe(false);
            expect(rejectedCheck).toBe(true);
        });
    });
});


describe("FileSource.getImageFromURL()", () => {
    
    beforeAll(function() {
        elementGenerator("getImageFromURL()");
    });

    afterAll(function() {
        elementRemover("getImageFromURL()");
    });
    
    let fileSource, serverResponse, responseBody, responseOptions;
    let resolvedCheck, rejectedCheck;

    beforeEach(function() {
        fileSource = new FileSource();

        responseBody = new File([], "fakeImage", {});
        responseOptions = {'headers': {'content-type': 'image/jpg'}};
        serverResponse = new Request(responseBody, responseOptions);
    });

    it("should return an image if provided a URL", () => {
        // LIVE TEST!
        // Calls through a real fetch request; won't work offline.
        const imageURL = "https://i1.sndcdn.com/artworks-vyMuu6DKlukpJLxY-3dBfmw-t500x500.jpg";
        const fileName = "dapper_horse.jpg";
        const fileType = "image/jpg";
        return fileSource.getImageFromURL(imageURL, fileName, fileType).then((file) => {
            expect(file).toEqual(jasmine.any(File));
            expect(file.name).toBe(fileName);
            expect(file.type).toBe(fileType);
        });
    });

    it("should return a random image if no URL/arguments is/are provided", () => {
        // LIVE TEST!
        // Calls through a real fetch request; won't work offline.
        spyOn(window, "makeFetch").and.callThrough();
        return fileSource.getImageFromURL().then((file) => {
            expect(window.makeFetch).toHaveBeenCalledWith("https://picsum.photos/300");
            expect(file).toEqual(jasmine.any(File));
            expect(file.name).toBe("image.jpg");
            expect(file.type).toBe("image/jpg");
        });
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


describe("FileSource.getPresignedURLPacket()", () => {
    const fileSource = new FileSource();
    let mockFile, serverResponse;

    beforeEach(function() {
        // create a fake file
        mockFile = new File([], 'mockFile.jpg', {type: 'image/jpg'});

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

describe("FileSource.processFile() and FileSource.processAllFiles()", () => {
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

        // spy on auxiliary method generateThumbnail
        spyOn(fileSource, "generateThumbnail").and.resolveTo(true);
        spyOn(fileSource, "refreshURLs");
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

describe("FileSource.refreshURLs()", () => {
    let fileSource;

    let selectElement, optionElement1, optionElement2, optionElement3;

    beforeAll(function() {
        elementGenerator("getImageFromURL()");
    });

    afterAll(function() {
        elementRemover("getImageFromURL()");
    });

    beforeEach(function() {
        fileSource = new FileSource();
        selectElement = fileSource.urlSelectElement;
        optionElement1 = optionElement2 = optionElement3 = document.createElement("option");
    });

    it("should add new URLs to the select element", () => {
        fileSource.processedImageURLs = ["fakeUrl1", "fakeUrl2", "fakeUrl3"];
        fileSource.refreshURLs();
        expect(selectElement.children.length).toBe(3);
    });

    it("should remove URLs from the select element", () => {
        // prepopulate select element
        selectElement.append(optionElement1, optionElement2, optionElement3);
        // set processedImageURLs to only have 1 elements
        fileSource.processedImageURLs = ["fakeUrl1"];
        fileSource.refreshURLs();
        expect(selectElement.children.length).toBe(1);      
    });

    it("should generate an error if select element doesn't exist", () => {
        fileSource.urlSelectElement = undefined;
        try {
            fileSource.refreshURLs();
        }
        catch(error) {
            expect(error).toEqual(jasmine.any(Error));
        }
        fileSource.urlSelectElement = selectElement;
    });
});


describe("FileSource.uploadFileToS3()", () => {
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