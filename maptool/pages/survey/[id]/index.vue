<template>
  <!-- Survey/index.vue -->
    <NuxtLayout name="default">
        <div class="padding-16">
          <v-sheet
            class="d-flex align-center flex-column" 
          >
          <v-card 
            class="my-card" 
            :title=survey.name
            :subtitle="'Open until:' + formatDate(survey.expire_date)"   
            >
            <template v-slot:text>
              <div class="description-style preserve-breaks">
                {{ survey.description }}
              </div>
            </template>
            <v-card-actions class="justify-center" >
              <v-btn @click="startSurvey" color="primary"  variant="elevated">
                <i class="fa-solid fa-play"></i>
                <span class="q-pa-sm">Start Survey</span>
              </v-btn>
            </v-card-actions>
          </v-card>
          </v-sheet>
        </div>
    </NuxtLayout>
</template>

<script setup>
import { ref } from "vue"
import { navigateTo } from "nuxt/app";
import { useResponseStore } from '~/stores/response'
import { useSurveyStore } from '~/stores/survey'
import { useUserStore } from '~/stores/user'
const storeResponse = useResponseStore()
const storeUser = useUserStore()
const survey_url = "/api/surveys/"
const create_response_url = "/api/responses/"
// const origin_url = "http://localhost:3000"
const data = ref([])
const route = useRoute()
// console.log('route id', route.params.id)
const survey = await storeResponse.getSurvey({ id: route.params.id })
// console.log('survey.value. in survey index //', survey.value.id)
const storeSurvey = useSurveyStore()


// Clear all answers in the Response store
storeResponse.clearAnswers()


const createResponse = async () => {
    // Make a POST request to your Django API endpoint to create a new Response object
    // await storeResponse.createResponse({ id: route.params.id })
    let respondent = null;
    if (storeUser.isAuthenticated) {
      respondent = 'http://localhost:8000/api/v2/' + user.value.userData.id 
  
    }
    const responseId = await storeResponse.createResponse({ survey_url: survey.value.url, respondent_url: respondent })
    
    // Navigate to the /survey/${survey.id}/1 page after the response is created
    if (responseId) {

      // console.log('response id //', responseId)
        // Navigate to the /survey/${survey.id}/1 page after the response is created
        return navigateTo('/survey/' + route.params.id )
    }

};

const getQuestions = async () => {
    // Make a GET request to your Django API endpoint to get the questions for the survey
    const questions = await storeSurvey.getQuestionsOfSurvey()
    // console.log('questions //', questions)
    // Navigate to the /survey/${survey.id}/1 page after the response is created
    // if (questions) {
    //     // Navigate to the /survey/${survey.id}/1 page after the response is created
    //     return navigateTo('/survey/' + route.params.id + '/' + survey.value.id)
    // }
    return questions
};

const startSurvey = async () => {
  await createResponse();
  const questions = await getQuestions();
  
  if (questions) {
    // Navigate to the /survey/${survey.id}/1 page after the response is created
    return navigateTo('/survey/' + survey.value.id + '/' + 1 ) // TODO: replace 1 with  question orden
}
};

// Clear all answers in the Response store
storeResponse.clearAnswers()
</script>

<style>
.preserve-breaks {
  white-space: pre-wrap;
}
.description-style {
  font-size: 15px; /* Example: Change the font size */
  color: #333; /* Example: Change the text color */
  /* Add more styles as needed */
}
</style>
