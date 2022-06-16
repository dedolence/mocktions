async function triggerUploads(e) {
    // determine source of file then initiate upload to S3 bucket
    const files = Array.from($('id_upload_image').files);
    const file = files[0];
    const url = $('id_url_image').value;
    const loading_modal = new bootstrap.Modal($('id_loading_image_modal'));
            
    loading_modal.show();
    
    // retrieve file from URL first if necessary
    const retrieveFiles = await new Promise((res, rej) => {
        if (file === undefined) {
            getFile(url)
            .then(file => {
                files.push(file);
            })
            .then(() => {
                res();
            })
            .catch((e) => {
                console.log(e);
                loading_modal.hide();
                $('id_image_errors').classList.remove('hide');
                $('id_image_errors').classList.add('show');
            })
        } else {
            res();
        }
    })

    promises = []
    for (const f of files) {
        // get signed url 
        const promise = getSignedUrlRequest(f)
        promises.push(promise);
        promise.then((signed_url) => {
                // get formatted html
                return getImageHtml(signed_url);
            })
            .then((image_html) => {
                const img_thumbnails = $('id_image_thumbnails');
                img_thumbnails.innerHTML += image_html;
            });
    }

    Promise.all(promises).then(() => {
        loading_modal.hide();
    });
}


function getImageHtml(image_url) {
    return new Promise((res, rej) => {
        const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = document.querySelector('[name=get_image_html]').value;
        
        fetch(url + "?image_url=" + image_url, {
            headers: {'X-CSRFToken': csrf_token}
        })
        .then((response) => { return response.json(); })
        .then((response) => { 
            res(response.html); 
        });
    });
}


function getFile(url) {
    // retrieve/create file from URL
    // source: https://newbedev.com/how-to-convert-dataurl-to-file-object-in-javascript
    if (!url) {
        url = "https://picsum.photos/300";
    }
    return fetch(url)
    .then((res) => {
        return res.arrayBuffer();
    })
    .then((buf) => {
        const file = new File([buf], 'image_upload.jpg', {type: 'image/jpg'});
        return file;
    })
    .catch((err) => {
        throw err;
    })
}


function getSignedUrlRequest(file) {
    return new Promise((res, rej) => {
        const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const post_data = new FormData();
              post_data.append('file_name', file.name);
              post_data.append('file_type', file.type);
        const url = document.querySelector('[name=sign_s3_url]').value;

        fetch(url, {
            method: "POST",
            body: post_data,
            headers: {'X-CSRFToken': csrf_token}
        }).then((response) => {
            if (response.status >= 200 && response.status <= 299) {
                return response.json();
            }
            else {
                throw Error(response.statusText);
            }
        }).then((json) => {
            res(uploadFile(file, json.data, json.image_url));
        })
    })
}


function uploadFile(file, data, image_url) {
    return new Promise((res, rej) => {
        const post_data = new FormData();
        for (key in data.fields) {
            post_data.append(key, data.fields[key]);
        }
        post_data.append('file', file);

        fetch(data.url, {
            method: "POST",
            body: post_data,
        }).then(() => {
            res(image_url);
        })
    })
}