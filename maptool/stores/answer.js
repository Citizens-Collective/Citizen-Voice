import { defineStore } from 'pinia';
import { useUserStore } from './user';
import { useGlobalStore } from './global';
import setRequestConfig from './utils/setRequestConfig';


export const useAnswerStore = defineStore('answer', {

    state: () =>
    // required data for the response store
    // responseId // if null it means that the respondent 
    // respondent
    // currentQuestion
    // surveyId
    // answersToCurrentSurvey
    {
        return {
            question_index: null,
            body: ""
        }
    },
    getters: {

    },
    actions: {
        updateAnswer(answer) {
            // updates an answer in the array of answers
            // answer must have the following structure
            // {
            // question_id: integer,
            // text: text,
            // }
            const existingAnswer = this.answers.find(a => a.question_id === answer.question_id);
            if (existingAnswer) {
                existingAnswer.text = answer.text;
            }
            else {
                this.answers.push(answer);
            }

        },

        clearAnswers() {
            // Clear all the answers
            this.answers = []
        },
        async submitAnswer(response_url, question_url, answer_value) {
            const user = useUserStore();
            const global = useGlobalStore();
            const csrftoken = user.getCookie('csrftoken');
            const token = user.getAuthToken;

            // Create FormData instead of JSON
            const formData = new FormData();
            formData.append('response', response_url);
            formData.append('question', question_url);
            formData.append('body', answer_value);

            const config = {
                headers: {
                    // Remove Content-Type to let browser set it automatically for FormData
                    'X-CSRFToken': csrftoken,
                },
                method: 'POST',
                // pas the data for the new Response object as the request body

                // TODO: have the repondent set to the logged in user 
                body: formData  // Use FormData instead of JSON
            };
            if (token) {
                config.headers['Authorization'] = `Token ${token}`
            };

            const { data: response, pending, error } = await useAsyncData('submitAnswer', () => $cmsApi('/answers/', config));

            if (response) {
                console.log('response submitted //> ');
            }

        }


    }
})