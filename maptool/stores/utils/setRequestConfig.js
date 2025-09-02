import { useUserStore } from '../user.js'

const setRequestConfig = (params = { method: "GET" }) => {
    const user = useUserStore()
    const csrftoken = user.getCookie('csrftoken');
    const token = user.getAuthToken

    const config = {
        headers: {
            'X-CSRFToken': csrftoken
        },
        ...params,
    }

    // Only set Content-Type for JSON if body is not FormData
    if (params.body && !(params.body instanceof FormData)) {
        config.headers['Content-Type'] = 'application/json';
    }

    if (token) {
        config.headers['Authorization'] = `Token ${token}`
    }

    return config
}

export default setRequestConfig