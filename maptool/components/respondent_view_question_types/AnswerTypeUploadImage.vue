<template>
  <v-container style="padding: 16px">
    <div class="image-upload-container">
      <!-- File input -->
      <v-file-input
        ref="fileInput"
        v-model="selectedFile"
        accept="image/*"
        label="Choose an image"
        prepend-icon="mdi-camera"
        show-size
        @change="handleFileSelect"
        :loading="uploading"
        :disabled="uploading"
        :rules="fileRules"
      />
      
      <!-- Upload button -->
      <v-btn
        v-if="selectedFile && !uploading"
        @click="uploadImage"
        color="primary"
        :loading="uploading"
        class="mt-2"
      >
        <v-icon left>mdi-upload</v-icon>
        Upload Image
      </v-btn>
      
      <!-- Image preview -->
      <div v-if="preview || answer.image_url" class="image-preview mt-4">
        <v-card>
          <v-img
            :src="preview || answer.image_url"
            alt="Image preview"
            max-height="300"
            contain
          />
          <v-card-actions>
            <v-btn
              v-if="answer.image_url"
              @click="removeImage"
              color="error"
              text
              small
            >
              <v-icon left>mdi-delete</v-icon>
              Remove Image
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
      
      <!-- Error message -->
      <v-alert
        v-if="errorMessage"
        type="error"
        dismissible
        class="mt-2"
        @input="errorMessage = null"
      >
        {{ errorMessage }}
      </v-alert>
      
      <!-- Success message -->
      <v-alert
        v-if="successMessage"
        type="success"
        dismissible
        class="mt-2"
        @input="successMessage = null"
      >
        {{ successMessage }}
      </v-alert>
    </div>
  </v-container>
</template>

<script>
export default {
  name: "ImageUploadAnswer",
}
</script>

<script setup>

import { useSurveyStore } from '~/stores/survey'
import { useResponseStore } from '~/stores/response';

const surveyStore = useSurveyStore();
const responseStore = useResponseStore();

const router = useRouter();

const emit = defineEmits(['updateAnswer'])
const props = defineProps({
  question_index: Number,
  question: Object,
  answer: Object
})

// Reactive data
const selectedFile = ref(null)
const preview = ref(null)
const uploading = ref(false)
const errorMessage = ref(null)
const successMessage = ref(null)

// File validation rules
const fileRules = [
  value => {
    if (!value) return true
    if (value.size > 5 * 1024 * 1024) {
      return 'Image size should be less than 5MB'
    }
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(value.type)) {
      return 'Please select a valid image file (JPEG, PNG, GIF, WebP)'
    }
    return true
  }
]

const current_question_index = router.currentRoute.value.params._question - 1; // Adjusting to zero-based index


// Handle file selection
function handleFileSelect(file) {
  if (!file) {
    preview.value = null
    return
  }
  
  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    preview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// Upload image to the server
async function uploadImage() {
  if (!selectedFile.value) return
  
  // Validate file
  const validation = fileRules[0](selectedFile.value)
  if (validation !== true) {
    errorMessage.value = validation
    return
  }
  
  uploading.value = true
  errorMessage.value = null
  
  try {
    // Create FormData for the upload
    const formData = new FormData()
    formData.append('question', props.question.url) // Use question URL as expected by your API
    formData.append('image', selectedFile.value)
    formData.append('response', responseStore.responseUrl) // Use the response URL from the store
    formData.append('mapview', null)

    console.log( 'responseurl', responseStore.responseUrl)
    
    // If you have a response ID, include it
    if (props.answer.response) {
      formData.append('response', props.answer.response)
    }
    
      // Make API call to upload image
    
    //TODO: CONTINUE HERE Replace this call with a call that includes the actual question url, response url and  mapview value (should be null)
    const response = await $cmsApi('/answers/upload_image_answer/', {
      method: 'POST',
      body: formData
    })
    
    // Update answer with the response
    props.answer.image_url = response.image
    props.answer.text = `Image uploaded: ${selectedFile.value.name}`
    
    // Emit the update
    emit('updateAnswer', props.answer, props.question_index)
    
    successMessage.value = 'Image uploaded successfully!'
    
  } catch (error) {
    console.error('Upload failed:', error)
    errorMessage.value = error.data?.message || 'Failed to upload image. Please try again.'
  } finally {
    uploading.value = false
  }
}

// Remove uploaded image
async function removeImage() {
  try {
    // You might want to call an API to delete the image
    // For now, just clear the local state
    props.answer.image_url = null
    props.answer.text = ''
    preview.value = null
    selectedFile.value = null
    
    emit('updateAnswer', props.answer, props.question_index)
    
    successMessage.value = 'Image removed successfully!'
    
  } catch (error) {
    console.error('Remove failed:', error)
    errorMessage.value = 'Failed to remove image. Please try again.'
  }
}

// Initialize component if answer already has an image
onMounted(() => {
  if (props.answer.image_url) {
    // Image already exists, no need to show file input as selected
    preview.value = null
  }
})
</script>

<style scoped>
.image-upload-container {
  max-width: 500px;
}

.image-preview {
  border: 2px dashed #ccc;
  border-radius: 4px;
  padding: 16px;
}

.v-file-input {
  margin-bottom: 16px;
}
</style>