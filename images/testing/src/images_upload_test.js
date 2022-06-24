/**
 * Copies the Jquery function to access DOM elements.
 * @param {String} element_id
 * @returns {HTMLElement} An HTMLElement
 */
const $ = function(element_id) {
    return document.getElementById(element_id);
}


/**
 * Handles user uploads of files (typically images). 
 * Users can upload from their hard drive or provide a URL.
 * @constructor
 * @property {...File} sourceFileArray Files to be uploaded
 */
function FileSource() {
    this.sourceFileArray = (() => {
        if ($('id_image_upload')) {
            return Array.from($('id_image_upload')).files;
        } else {
            return [];
        }
    })();
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
 * @param {File} sourceFile 
 * 
 * @returns {PresignedURLPacket} 
 * A {@link PresignedURLPacket} sent from AWS required for uploading file.
 */
FileSource.prototype.getPresignedURLPacket = function(sourceFile) {
    return new Promise((res, rej) => {
        const url = document.querySelector('[name=sign_s3_url]').value
            + "?name=" + sourceFile.name + "type=" + sourceFile.type;

        makeFetch(url)
        .then((response) => {
            return response.json();
        })
        .then((json) => {
            // return the presigned url packet for uploading
            res(
                {
                    file: sourceFile,       // File object
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
 * Simple image retriever.
 * 
 * @source https://newbedev.com/how-to-convert-dataurl-to-file-object-in-javascript
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
 * @returns {File}
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
        })
    })
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