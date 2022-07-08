// SETUP: 
// Add a beforeAll() to each suite that calls elementGenerator();
// Add an afterAll() to each suite that calls elementRemover();

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
];


/**
 * Returns an object of element parameters to their IDs.
 */
const ids = Object.fromEntries(elements.map((e) => { return [e.id, e.id] }));

/**
 * Iterates through the elements array and creates/appends each to DOM.
 * @returns {void}
 */
function elementGenerator() {
    return new Promise((res, rej) => {
        promises = [];
        for (el of elements) {
            promises.push(new Promise((rslve, rjct) => {
                let _ = document.createElement(el.node);
                _.id = el.id;
                if (el.type) {
                    _.type = el.type;
                }
                _.classList.add("tempDOMelement");  // for removing later
                document.body.appendChild(_);
                rslve();
            }));
        }
        Promise.all(promises).then(() => {
            res();
        })
    });
}
/* function elementGenerator(caller) {
    return new Promise((res, rej) => {
        //console.log("Generating elements for " + caller);
        for (el of elements) {
            //console.log("--- generating element with ID " + el.id);
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
} */

/**
 * Removes all elements with class "tempDOMelement" from DOM.
 * @returns {void}
 */
function elementRemover(caller) {
    //console.log("Removing elements for " + caller);
    let nodes = document.querySelectorAll(".tempDOMelement");
    for (node of nodes) {
        //console.log("--- Removing node: " + node.id);
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

describe("FileSource.getImageFromURL()", () => {
    
    beforeAll(function() {
        elementGenerator("getImageFromURL()");
    });

    afterAll(function() {
        elementRemover("getImageFromURL()");
    });

    const fileSource = new FileSource();
    
    let serverResponse, responseBody, responseOptions;
    let resolvedCheck, rejectedCheck;

    beforeEach(function() {
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


describe("FileSource.generateThumbnail()", () => {
    let div;
    beforeAll(async function() {
        await elementGenerator("generateThumbnail()");
    });

    afterAll(function() {
        elementRemover("generateThumbnail()");
    });

    const fileSource = new FileSource("generateThumbnail");

    it("should be true", function() {
        expect(true).toBe(true);
    });
    let imageUrl, thumbnailElement, response, responseBody, responseOptions;
   
    beforeEach(function() {

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
            expect(window.getAJAXURL).toHaveBeenCalledWith("imageThumbnail");
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