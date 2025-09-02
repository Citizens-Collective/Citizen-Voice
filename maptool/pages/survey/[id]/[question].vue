<template>
    <NuxtLayout name="default">
        <div class="">
            <!-- Question card: number & text -->
            <v-card class="my-card">
            <template v-slot:title>
                    <div class="title-wrapper" style="white-space: normal;">
                        {{ question.text }}
                    </div>
            </template>
            <template v-slot:subtitle>
                    <div class="title-wrapper" style="white-space: normal;">
                        {{ question.explanation}}
                    </div>
            </template>
                <!-- Answer card-->
                <div v-if="question.has_text_input" class="my-card col">
                    <RespondentViewQuestionTypesAnswerTypeText 
                    v-if="question.question_type === 'text'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeShortText 
                    v-if="question.question_type === 'short-text'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeSelect
                    v-if="question.question_type === 'radio'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeMultiselect
                     v-if="question.question_type === 'select-multiple'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                     />
                    <RespondentViewQuestionTypesAnswerTypeDate 
                    v-if="question.question_type === 'date'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeInteger 
                    v-if="(question.question_type === 'integer' || 
                        question.question_type === 'float')" 
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeUploadImage
                    v-if="question.question_type === 'image-upload'"
                    :question="question"
                    :question_index="current_question_index"
                    :answer="current_answer"
                    @update-answer="handleUpdateAnswer"
                    />
                    <RespondentViewQuestionTypesAnswerTypeLikertScale
                    v-if="question.question_type === 'likert-scale'"
                    :question="question"
                    :answer="answer"
                    :question_index="current_question_index"
                    @update-answer="handleUpdateAnswer"
                    />
                </div>

                <div class="q-pa-md row items-start q-gutter-md">
                    <!-- Map card -->
                    <div v-if="(question.mapview != null )" style="min-width: 600px;"
                        class="my-card col">
                        <MapView
                        :mapViewUrl ="question.mapview" 
                        />
                    </div>
                    <!-- Navigation -->
                    <v-card-actions>
                        <v-btn v-show="current_question_index > 1" @click="prevQuestion" color="primary" variant="outlined">
                            <i class="fa-solid fa-arrow-left"></i>
                            <span class="q-pa-sm">Previous Question</span>
                        </v-btn>
                        <v-btn v-show="survey_store.questionCount != current_question_index" @click="nextQuestion" color="primary" variant="outlined">
                            <i class="fa-solid fa-arrow-right"></i>
                            <span class="q-pa-sm">Next Question</span>
                        </v-btn>
                                <v-btn v-show="survey_store.questionCount == current_question_index" @click="submitAnswers" color="primary" variant="flat">
                                    <i class="fa-solid fa-check"></i>
                                    <span class="q-pa-sm">Submit</span>
                                </v-btn>
                    </v-card-actions>
                </div>
            </v-card>
        </div>

    </NuxtLayout>
</template>


<script setup>
import { ref, watch } from "vue"
import { navigateTo } from "nuxt/app";
import { useSurveyStore } from "~/stores/survey";
import { useResponseStore } from '~/stores/response';
import { useMapViewStore } from "~/stores/mapview";
import { useGlobalStore } from "~/stores/global";

// import leaflet from "leaflet"
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LCircle, LControl } from "@vue-leaflet/vue-leaflet";

const responseStore = useResponseStore();
const mapViewStore = useMapViewStore();

mapViewStore.$reset();

const route = useRoute();
const survey_store = useSurveyStore();
const questions = survey_store.questions;

// Here, we use the list of questions in the survey store to display questions according to the order
// specified when the survey was created. We use the numbers in the URL to navigate between questions
// while maintaining the order of the questions in the survey store. 
var current_question_index = parseInt(route.params.question, 10); // use url questions id as an index to load each question 
let current_question_url = questions[current_question_index - 1].url;  // gets the id for the questions
let current_mapview_id = questions[current_question_index - 1].mapview;  // gets the value for the map view
let question = questions[current_question_index - 1];

// Replace with your actual answer object
const current_answer = ref({ question_url: current_question_url, text: '', mapview: {} });
// const answers = ref({ text: body });  // body of the answer must be a string (as per the API)
// ref makes the variable reactive
const handleUpdateAnswer = (updatedAnswer, questionIndex) =>{
      // Handle the updated answer here
    // console.log(updatedAnswer);
    current_answer.text = updatedAnswer;
    current_answer.question_index = questionIndex;
    const current_mapview = mapViewStore.getMapViewAnswer;
    current_answer.mapview = current_mapview;
    responseStore.updateAnswer(updatedAnswer);
    };


const circles = ref([]) // this is what user will add
let circleClickedAndRemoved = false
let resetClicked = false

// to navigate from one question to the previous/next
const prevQuestion = async () => {
    // if this is not the first question:
    let question_to_navigate = (parseInt(route.params.question, 10) - 1)
    if (question_to_navigate != 0) {
        return navigateTo('/survey/' + route.params.id + '/' + question_to_navigate)
    } else {
        return navigateTo('/survey/' + route.params.id)
    }
}

const nextQuestion = async () => {
    // if this is not the last question:
    return navigateTo('/survey/' + route.params.id + '/' + (parseInt(route.params.question, 10) + 1))
}


const submitAnswers = async () => {
    
    const global = useGlobalStore();

    for (let i = 0; i < responseStore.answers.length; i++) {
        let response_url = responseStore.responseUrl;
        let question_url = responseStore.answers[i].question_url;
        let mapview_url = responseStore.answers[i].mapview.url;
        const answer_text = responseStore.answers[i].text;
        responseStore.submitAnswer(
            response_url,
            question_url,
            answer_text,
            mapview_url
        )
    }
    global.succes("Your answers have been submitted")
    return navigateTo('/submitted/')
    
};

// inspired by Roy J's solution on Stack Overflow:
// https://stackoverflow.com/questions/54499070/leaflet-and-vuejs-how-to-add-a-new-marker-onclick-in-the-map
const removeCircle = async (index) => {
    // console.log("removeCircle function called")
    circles._value.splice(index, 1)
    circleClickedAndRemoved = true
}

const addCircle = async (event) => {
    if (circleClickedAndRemoved) {
        circleClickedAndRemoved = false
    } else if (resetClicked) {
        resetClicked = false
    } else {
        // console.log("addCircle function called")
        circles._value.push(
            [event.latlng.lat, event.latlng.lng]
        )
    }
}
const resetMap = async () => {
    // console.log("resetMap function called")
    circles._value.splice(0, circles._value.length)
    // TODO: reset map center and zoom level based on mapview
    resetClicked = true
}



</script>

<style lang="scss">
#map {
    height: 180px;
}
</style>