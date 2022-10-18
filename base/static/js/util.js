/**
 * Copies the Jquery function to access DOM elements. Deffaults to an
 * ID selection if no selector is provided. Currently doesn't work with
 * multiple selections.
 * 
 * @param {String} selector
 * 
 * @returns {HTMLElement} 
 */
const $ = function(selector) {
    const cssSelectors = ['.', '#'];
    if (!cssSelectors.includes(selector[0])) {
        return $('#' + selector);
    } else {
        return document.querySelector(selector);
    }
}


/**
 * Returns the appropriate URL for an AJAX request, including query strings.
 * In the future I'll probably have a script that loads all URLs
 * to an object and pull from those. That would be easy enough with a context
 * variable and context processor in Django. For now it is hard-coded.
 * @param {String} func 
 *  A string keyword that maps to a particular AJAX URL. I'd like to come up
 *  with a cooler way of doing this.
 * @param {Object} params
 *  For appending keys/values to a URL for a GET request.
 * @returns {String} url
 */
function getAjaxUrl(func, params=null) {
    let url;
    switch(func) {
        case "deleteImage":
            url = "delete_image";
            break;
        case "imageThumbnail":
            url = "get_image_html";
            break;
        case "presignedURL":
            url = "sign_s3";
            break;
        default:
            url = "default_url";
            break;
    }
    if (params) {
        let extras = '?';
        for (const param in params) {
            extras += param + "=" + encodeURIComponent(params[param]) + "&";
        }
        extras = extras.slice(0, -1); // remove trailing &, not important
        url += extras;
    }
    return url;
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


/**
 * Handles server error by either updating the UI or logging.
 * @param {Error} error 
 * @returns {Error}
 */
 function handleFetchError(error) {
    const errorDisplayAlert = $('errorDisplay');
    const errorMessage = "There was an error with your request:";
    if (!errorDisplayAlert) {
        console.log(errorMessage, error);
    } else {
        errorDisplayAlert.innerHTML = errorMessage + "<br/>" + error;
    }
    return error;
}


/**
 * An object describing the optional parameters for a fetch() request
 * @typedef {Object} FetchOptions
 * @property {String} method
 *  GET or POST
 * @property {FormData} body
 *  Body of request.
 * @property {Object} headers 
 *  Standard HTTP request headers.
 */

/**
 * Using this instead of the built-in fetch() API in order to provide better
 * error-handling.
 * @async 
 * @param {String} url 
 *  Points to the server path to use for a fetch() request
 * @param {FetchOptions} options 
 *  The same options object normally included in a fetch() request.
 * @returns {Promise<Response>}
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
            // don't reject to handleFetchError(). instead, reject normally
            // so that the calling method can choose how to handle the rejection.
            rej(error);
        })
    });
}