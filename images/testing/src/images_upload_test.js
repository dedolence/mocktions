"use strict";

/**
 * Handles user uploads of files (typically images). 
 * Users can upload from their hard drive or provide a URL.
 * @constructor
 * @property {Array<PresignedURLPacket>} presignedURLPackets
 *  Objects returned from the server's S3 request, to be used for uploading file.
 * @property {Array<String>} processedImageURLs 
 *  The URLs to images that have been fully processed and uploaded.
 * @property {Array<File>} sourceFileArray 
 *  Files to be uploaded
 * @property {String} sourceURL
 *  A user-provided URL that points to an image to be uploaded
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
 * @async
 * @returns {Array<PresignedURLPacket>}
 */
 FileSource.prototype.collectImages = async function() {
    let image;

    // get image URL if provided
    if ($('id_image_url').value) {
        this.sourceURL = $('id_image_url').value;
    } else {
        this.sourceURL = "https://picsum.photos/300";
    }

    // get source files to be uploaded, if any.
    if ($('id_image_upload')) {
        this.sourceFileArray = Array.from($('id_image_upload')).files;
        return this.sourceFileArray;
    } else {
        image = await this.getImageFromURL(this.sourceURL);
        this.sourceFileArray = [image];
        return this.sourceFileArray;
    }
}


/**
 * Simple image retriever. Technically this would work for any file type but it's
 * intended for images.
 * @source https://newbedev.com/how-to-convert-dataurl-to-file-object-in-javascript
 * @async
 * @param {String} url 
 *  Optional. Points to the image to be retrieved. Defaults to a random image API.
 * @param {String} fileName 
 *  Optional. When uploaded to S3, filename gets randomized to a UUID hex.
 * @param {String} fileType
 *  Optional. MIME-Type.
 * @returns {Promise<File>} A Javascript File object containing the new image.
 */
 FileSource.prototype.getImageFromURL = function(
    url="https://picsum.photos/300",
    fileName="image.jpg",
    fileType="image/jpg") {
    
    const validTypes = ['image/jpg', 'image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    return new Promise((res, rej) => {
        let buffer, file;

        makeFetch(url)
        .then((response) => {
            // check valid content type
            const contentType = response.headers.get('content-type');
            if (!validTypes.includes(contentType)) {
                rej(handleFetchError(new Error("Invalid image type: " + contentType)));
            } else {
                buffer = response.arrayBuffer();
                file = new File([buffer], fileName, {type: fileType});
                res(file);
            }
        })
        .catch((error) => {
            rej(handleFetchError(error));
        });
    });
}


/**
 * Requests a formatted chunk of URL from the server to append to DOM.
 * Server responds with a JSON object with an html property.
 * @async
 * @param {String} url 
 *  The image src
 * @returns {Promise}
 */
FileSource.prototype.generateThumbnail = function(imageURL) {
    return new Promise((res, rej) => {
        let html, thumbCont, div;
        const fetchURL = getAJAXURL("imageThumbnail") + "?url=" + imageURL;
        makeFetch(fetchURL)
        .then((response) => {
            // clone may only be necessary in testing since i'm reusing a response
            // object for every makeFetch call.
            return response.clone().json();
        })
        .then((response) => {
            html = response.html;
            try {
                thumbCont = $('id_image_thumbnails');
                thumbCont.innerHTML += html;
                res();
            }
            catch(err) {
                rej(new Error("No place to put image thumbnails!", err));
            }
        })
        .catch((error) => {
            console.log("Error in generating thumbnail: ", error);
        })
    });
}


/**
 * An object returned by AWS containing relevant information for uploading a
 * file to an S3 bucket.
 * @typedef     {Object}   PresignedURLPacket
 * @property    {File}     file 
 *  The original File object.
 * @property    {S3Data}   data 
 *  Object returned by AWS needs to be included when uploading.
 * @property    {String}   url This 
 *  will be the location of the image once uploaded to S3.
 */

/**
 * An object returned by AWS that is required for uploading files to S3 bucket.
 * @source AWS
 * @typedef {object} S3Data
 */

/**
 * AJAX request for a presigned URL to be used for uploading a file to S3 bucket.
 * @async
 * @param {File} file 
 *  The file that we are retrieving the presigned URL for in order to upload.
 * @returns {Promise<PresignedURLPacket>} 
 *  A {@link PresignedURLPacket} sent from AWS required for uploading file.
 */
 FileSource.prototype.getPresignedURLPacket = function(file) {
    return new Promise((res, rej) => {
        const fetchURL = getAJAXURL('presignedURL') 
            + "?name=" + file.name + "type=" + file.type;

        makeFetch(fetchURL)
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
 * Handles the complete upload cycle for a single file. Retrieves a
 * presigned URL, uploads file, and returns the URL of the image.
 * @async
 * @param {File} file 
 * @returns {String} 
 *  URL of the file where it exists in the S3 bucket.
 */
FileSource.prototype.processFile = function(file) {
    return new Promise((res, rej) => {
        let url;

        this.getPresignedURLPacket(file)
        .then((packet) => {
            url = this.uploadFileToS3(packet.file, packet.data, packet.url);
            this.generateThumbnail(url);
            //this.appendImageURLToForm(url);
            res(url);
        })
        .catch((error) => {
            rej(handleFetchError(error));
        })
    });
}


/**
 * Takes all the files contained in sourceFileArray and uploads them to S3.
 * @async
 * @returns {Promise}
 */
FileSource.prototype.processAllFiles = function() {
    return new Promise((res, rej) => {
        // first gather files to upload
        this.collectImages()
        .then((sourceFiles) => {
            let modal, promises;

            // just make sure there are files to upload
            if(sourceFiles.length === 0 && this.sourceFileArray.length === 0) {
                rej();
            }
            
            // display a loading modal
            try {
                modal = new bootstrap.Modal($('id_loading_image_modal'));
                modal.show();
            }
            catch(err) {
                modal = { hide: () => { return; } };
            }

            // keep track of the promises by pushing them to an array
            promises = [];
            for (const file of sourceFiles) {
                promises.push(this.processFile(file));
            }

            // when all promises are ready, turn off loading modal
            Promise.all(promises).then((urls) => {
                this.processedImageURLs = urls;
                modal.hide();
                res();
            });
        })
    });
}


/**
 * Takes the information from the presigned URL as well as the File and sends
 * them to AWS. If the request goes through, this method returns the URL of the
 * file where it exists in the S3 bucket.
 * @async
 * @param {File} file 
 *  The original source file to be uploaded.
 * @param {S3Data} data 
 *  An object returned by AWS, retrieved when the pre-signed URL was generated.
 * @param {String} url 
 *  The location of the file on the S3 bucket, already determined when the 
 *  presigned URL was generated.
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