import { useResponseStore } from '~/stores/response';
import { useSurveyStore } from '~/stores/survey';
import { useMapViewStore } from '~/stores/mapview';
import { useAnswerMapViewStore } from '~/stores/answerMapview';
// Import other stores as needed

export const resetSurveySession = () => {
    const responseStore = useResponseStore();
    const surveyStore = useSurveyStore();
    const mapViewStore = useMapViewStore();
    const answerMapViewStore = useAnswerMapViewStore();

    // Reset all survey-related stores
    responseStore.$reset();
    surveyStore.$reset();
    mapViewStore.$reset();
    answerMapViewStore.$reset();

    console.log('All survey stores have been reset');
};

// New utility function for initializing a new survey session
export const initializeSurveySession = async (surveyId) => {
    const responseStore = useResponseStore();
    const surveyStore = useSurveyStore();
    const mapViewStore = useMapViewStore();
    const answerMapViewStore = useAnswerMapViewStore();

    // Reset all stores first
    resetSurveySession();
    
    // Set the current survey
    surveyStore.selectSurvey(surveyId);
    
    console.log(`Survey session initialized for survey ID: ${surveyId}`);
};