const $ = function(element_id) {
    return document.getElementById(element_id);
}


function FileSource() {
    // array of File objects to be uploaded
    this.fileArray = (() => {
        if ($('id_image_upload')) {
            return Array.from($('id_image_upload')).files;
        } else {
            return [];
        }
    })();
}

FileSource.prototype.getImageFromURL = async (
    url="https://picsum.photos/300", 
    fileName="image.jpg", 
    fileType="image/jpg") => {
    // used to download images from a 3rd-party website
    // source: https://newbedev.com/how-to-convert-dataurl-to-file-object-in-javascript
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


/* async function fetchFile(url, formData, options) {
    // a generic fetch method
    const csrf_token = getCSRFToken();
    return fetch(url, {
        method: options.method,
        body: formData,
        headers: {'X-CSRFToken': csrf_token}
    })
    .then(res => {
        // if the server response is good, return data in the format specified
        if (res.status >= 200 && res.status <= 299) {
            let data;
            switch (options.format) {
                case "json":
                    data = res.json();
                    break;
                case "arrayBuffer":
                    data = res.arrayBuffer();
                    break;
                default:
                    data = res;
                    break;
            }
            return data;
        }
        else {
            throw Error(res.statusText);
        }
    })
    .catch(() => {
        // this catches 4xx and 5xx errors
        // return a rejected promise so i can catch() it elsewhere
        return new Promise((res, rej) => {
            rej();
        })
    })
} */


function getCSRFToken() {
    if (document.querySelector('[name=csrfmiddlewaretoken]')) {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    else {
        return "replace_this_with_some_error_condition";
    }
}