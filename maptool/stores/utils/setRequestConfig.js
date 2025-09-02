import { useUserStore } from '../user.js'

const setRequestConfig = (params = { method: "GET" }) => {
    const user = useUserStore()
    const csrftoken = user.getCookie('csrftoken');
    const token = user.getAuthToken

    const config = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        ...params,
    }

    if (token) {
        config.headers['Authorization'] = `Token ${token}`
    }

    return config
}

export default setRequestConfig