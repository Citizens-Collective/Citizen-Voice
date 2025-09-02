import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { useGlobalStore } from './global'
import setRequestConfig from './utils/setRequestConfig';

export const useSurveyStore = defineStore('survey', {
    state: () => {
        return {
            selectedSurveyId: null,
            currentSurveyDesign: [],
            questions: [],
        }
    },
    getters: {
        questionCount() {
            return this.questions.length
        },
        getMapViewUrl(index) {
            return this.questions[index].map_view
        }
    },
    actions: {
        async getSurvey(suvery_url) {
            const user = useUserStore()
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'GET',
                // pathParams: () => ({ url: suvery_url.value })
            }

            if (token) {
                config.headers['Authorization'] = `Token ${token}`
            }

            const data = await useAsyncData(() => $cmsApi(suvery_url, config));

            return data
        },
        
        selectSurvey(id) {
            this.selectedSurveyId = id
        },

        async getSurveys() {
            const user = useUserStore()
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'GET',
            }


            if (token) {
                config.headers['Authorization'] = `Token ${token}`
            }
            const { data, error} = await useAsyncData('surveys', () => $cmsApi('/surveys', config));

            return { data, error }
        },

        /**
        * Create survey
        * @param {*} name
        * @param {*} description
        * @param {*} publish_date
        * @param {*} expire_date
        * @param {id} id
        */

        /**
         * Create a new survey based on the passed parameters
         */
        async createSurvey(
            name,
            description,
            publish_date,
            expire_date
        ) {
            const user = useUserStore()
            const global = useGlobalStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                method: 'POST',
                body: {
                    name,
                    description,
                    publish_date,
                    expire_date
                },
            }

            if (token) {
                config.headers['Authorization'] = `Token ${token}`

            }

            const { data: register, pending, error } = await useAsyncData('createSurvey', () => $cmsApi('/surveys/create-survey', config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                // console.log(warnMessage)
                return null

            }
           
            if (register?.value) {
                // Notification
                global.succes('createSurvey complete')
                this.id = register.value.id
                return register.value
            }

            return this.id
        },

        /**
                * Create a new survey based on the passed parameters
                */
        async updateSurvey(
            id,
            body
        ) {
            const global = useGlobalStore()
            const config = setRequestConfig({ method: 'PATCH', body: { ...body } })

            const { data: register, pending, error } = await useAsyncData('updateSurvey', () => $cmsApi(`/surveys/${id}/`, config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                // console.log(warnMessage)
                return null

            }
            if (register?.value) {
                // Notification
                global.succes('Updated')
                return register.value
            }
        },
        /**
         * Get surveys of the current user
         */
        async getSurveysOfCurrentUser() {
            const user = useUserStore()
            await user.loadUser()
            const global = useGlobalStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                method: 'GET'
            }

            if (token) {
                config.headers['Authorization'] = `Token ${token}`
            }

            const response = await useAsyncData('getSurveys', () => $cmsApi('/surveys/my-surveys', config))

            const error = response.error
            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
            }
            else {
            }

            return response
        },

        /**
         * Delete an existing survey based on the passed ID
         */
        async deleteSurvey(
            id
        ) {
            const user = useUserStore()
            const global = useGlobalStore()
            const csrftoken = user.getCookie('csrftoken');
            const token = user.userData.token

            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                method: 'DELETE'
            }


            if (token) {
                config.headers['Authorization'] = `Token ${token}`
            }

            const { data: register, pending, error } = await useAsyncData('deleteSurvey', () => $cmsApi('/surveys/' + id, config))

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)

            }
            else {
                // Notification
                global.succes('deleteSurvey complete')
                this.id = 1
                await navigateTo('/design')
            }

        },

        async getQuestionsOfSurvey() {
            const user = useUserStore();
            const global = useGlobalStore();
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken;

            const config = setRequestConfig({
                method: 'GET'
            });

            const id = this.selectedSurveyId
            // console.log('id in get questions//> ', id);

            // if (!this.questions){
                const { data: response, pending, error} = await useAsyncData(() => $cmsApi('/surveys/' + id + '/questions', config));
            
                const responseData = await response.value;  

                 
                this.questions = responseData;
                // console.log('Questions //> ', responseData);
            // }

              if (error.value){
                console.log('error in get questions //> ', error.value);
              };
            
            return responseData;
        },
    }
})
