/**
 * Copies the Jquery function to access DOM elements.
 * 
 * @param {String} element_id
 * 
 * @returns {HTMLElement} An HTMLElement
 */
const $ = function(element_id) {
    return document.getElementById(element_id);
}


/**
 * Handles user uploads of files (typically images). 
 * Users can upload from their hard drive or provide a URL.
 * 
 * @constructor
 * 
 * @property {Array<PresignedURLPacket>} presignedURLPackets
 * Objects returned from the server's S3 request, to be used for uploading file.
 * 
 * @property {Array<String>} processedImageURLs 
 * The URLs to images that have been fully processed and uploaded.
 * 
 * @property {Array<File>} sourceFileArray 
 * Files to be uploaded
 * 
 * @property {String} sourceURL
 * A user-provided URL that points to an image to be uploaded
 */
function FileSource() {
    this.presignedURLPackets = [];
    this.processedImageURLs = [];
    this.sourceFileArray = [];
    this.sourceURL;
}


/**
 * Looks for files uploaded to a file input first, defaults to a URL if none.
 * The URL itself defaults to a random image API, so sourceFileArray will always
 * contain at least one image file. 
 * 
 * @returns {Array<PresignedURLPacket>}
 */
 FileSource.prototype.collectFiles = async function() {
    // get image URL if provided
    if ($('id_image_url')) {
        this.sourceURL = $('id_image_url').value;
    } else {
        this.sourceURL = "https://picsum.photos/300";
    }

    // get source files to be uploaded, if any.
    if ($('id_image_upload')) {
        this.sourceFileArray = Array.from($('id_image_upload')).files;
        return this.sourceFileArray;
    } else {
        let image = await this.getImageFromURL(this.sourceURL);
        this.sourceFileArray = [image];
        return this.sourceFileArray;
    }
}


/**
 * Handles the complete upload cycle for a single file. Retrieves a
 * presigned URL, uploads file, and returns the URL of the image.
 * @async
 * 
 * @param {File} file 
 * 
 * @returns {String} URL of the file where it exists in the S3 bucket.
 * 
 */
FileSource.prototype.processFile = async function(file) {
    const packet = await this.getPresignedURLPacket(file);
    const url = await this.uploadFileToS3(packet.file, packet.data, packet.url);
    return url;
}


/**
 * Takes all the files contained in sourceFileArray and uploads them to S3.
 * 
 * @async
 * 
 * @returns {void}
 */
FileSource.prototype.processAllFiles = async function() {
    let promises = [];
    for (file of this.sourceFileArray) {
        promises.push(this.processFile(file));
    }

    this.processedImageURLs = await Promise.all(promises);
}


/**
 * An object returned by AWS containing relevant information for uploading a
 * file to an S3 bucket.
 * @typedef     {Object}   PresignedURLPacket
 * 
 * @property    {File}     file 
 * The original File object.
 * 
 * @property    {S3Data}   data 
 * Object returned by AWS needs to be included when uploading.
 * 
 * @property    {String}   url This 
 * will be the location of the image once uploaded to S3.
 */

/**
 * An object returned by AWS that is required for uploading files to S3 bucket.
 * @source AWS
 * @typedef {object} S3Data
 */

/**
 * AJAX request for a presigned URL to be used for uploading a file to S3 bucket.
 * 
 * @async
 * 
 * @param {File} file 
 * The file that we are retrieving the presigned URL for in order to upload.
 * 
 * @returns {Promise<PresignedURLPacket>} 
 * A {@link PresignedURLPacket} sent from AWS required for uploading file.
 */
FileSource.prototype.getPresignedURLPacket = function(file) {
    return new Promise((res, rej) => {
        const url = document.querySelector('[name=sign_s3_url]').value
            + "?name=" + file.name + "type=" + file.type;

        makeFetch(url)
        .then((response) => {
            return response.json();
        })
        .then((json) => {
            // return the presigned url packet for uploading
            res(
                {
                    file: file,       // File object
                    data: json.data,        // {} containing additional information 
                    url: json.image_url     // the URL of the file once it's uploaded
                }
            );
        })
        .catch((error) => {
            rej(handleFetchError(error));
        });
    });
}


/**
 * Simple image retriever. Technically this would work for any file type but it's
 * intended for images.
 * 
 * @source https://newbedev.com/how-to-convert-dataurl-to-file-object-in-javascript
 * 
 * @async
 * 
 * @param {String} url 
 * Optional. Points to the image to be retrieved. Defaults to a random image API.
 * 
 * @param {String} fileName 
 * Optional. When uploaded to S3, filename gets randomized to a UUID hex.
 * 
 * @param {String} fileType
 * Optional. MIME-Type.
 * 
 * @returns {Promise<File>} A Javascript File object containing the new image.
 */
FileSource.prototype.getImageFromURL = function(
    url="https://picsum.photos/300",
    fileName="image.jpg",
    fileType="image/jpg") {
    return new Promise((res, rej) => {
        makeFetch(url)
        .then((response) => {
            let buffer = response.arrayBuffer();
            let file = new File([buffer], fileName, {type: fileType});
            res(file);
        })
        .catch((error) => {
            rej(error);
        });
    })
}


/**
 * Takes the information from the presigned URL as well as the File and sends
 * them to AWS. If the request goes through, this method returns the URL of the
 * file where it exists in the S3 bucket.
 * 
 * @async
 * 
 * @param {File} file 
 * The original source file to be uploaded.
 * 
 * @param {S3Data} data 
 * An object returned by AWS, retrieved when the pre-signed URL was generated.
 * 
 * @param {String} url 
 * The location of the file on the S3 bucket, already determined when the 
 * presigned URL was generated.
 * 
 * @returns {Promise<String>} The same url as in the parameters.
 */
FileSource.prototype.uploadFileToS3 = function(file, data, url) {
    return new Promise((res, rej) => {
        const postData = new FormData();
        // all fields need to be copied into the post body
        for (key in data.fields) {
            postData.append(key, data.fields[key]);
        }
        postData.append('file', file);
        
        makeFetch(data.url, {
            method: "POST",
            body: postData
        })
        .then(() => {
            res(url);
        })
        .catch((error) => {
            rej(handleFetchError(error));
        });
    });
}


/**
 * An object describing the optional parameters for a fetch() request
 * 
 * @typedef {Object} FetchOptions
 * 
 * @property {String} method
 * GET or POST
 * 
 * @property {FormData} body
 * Body of request.
 * 
 * @property {Object} headers 
 * Standard HTTP request headers.
 */

/**
 * Using this instead of the built-in fetch() API in order to provide better
 * error-handling.
 * 
 * @param {String} url Points to the server path to use for a fetch() request
 * @param {FetchOptions} options 
 * @returns {Response}
 */
function makeFetch(url, options={}) {
    /*
    options = { method:, body:, headers:, etc.} (from vanilla fetch() api)
    */
    return new Promise((res, rej) => {
        fetch(url, options)
        .then((response) => {
            if (response.status >= 200 && response.status <= 299) {
                // request is ok, resolve response
                res(response);
            }
            else {
                throw new Error(response.statusText);
            }
        })
        .catch((error) => {
            rej(error);
        })
    });
}


/**
 * Handles server error by either updating the UI or logging.
 * @param {Error} error 
 * @returns {Error}
 */
function handleFetchError(error) {
    const errorDisplayAlert = $('errorDisplay');
    const errorMessage = "There was an error handling fetch request:";
    if (!errorDisplayAlert) {
        console.log(errorMessage, error);
    } else {
        errorDisplayAlert.innerHTML = errorMessage + "<br/>" + error;
    }
    return error;
}


/**
 * Searches the DOM for a hidden form input containing the session's CSRF token.
 * @returns {String}
 */
function getCSRFToken() {
    if (document.querySelector('[name=csrfmiddlewaretoken]')) {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    else {
        return "replace_this_with_some_error_condition";
    }
}