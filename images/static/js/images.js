async function triggerUploads(e) {
    // determine source of file then initiate upload to S3 bucket
    const files = Array.from($('id_upload_image').files);
    const file = files[0];
    const url = $('id_url_image').value;
    const loading_modal = new bootstrap.Modal($('id_loading_image_modal'));
            
    loading_modal.show();
    
    const retrieveFiles = await new Promise((res, rej) => {
        if (file === undefined) {
            // no files provided to upload, so halt operation 
            // to retrieve file from a 3rd party website.
            let getFileRequest = getFile(url);
            getFileRequest
            .then(file => {
                files.push(file);
            })
            .then(() => {
                res();
            })
            .catch((e) => {
                console.log(e);
                return false;
            })
        } else {
            res();
        }
    })

    const requests = []
    for (const f of files) {
        const url = await getSignedUrlRequest(f);
        addImageToPage(url);
        requests.push(url);
    }
    
    Promise.all(requests).then(() => {
        loading_modal.hide();
    });

}


function addImageToPage(url) {
    const image_element = document.createElement('img');
          image_element.classList.add('img-thumbnail');
          image_element.alt = "A user-uploaded image";
          image_element.src = url;

    $('id_image_thumbnails').appendChild(image_element);
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
        // Probably a CORS problem
        throw e;
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