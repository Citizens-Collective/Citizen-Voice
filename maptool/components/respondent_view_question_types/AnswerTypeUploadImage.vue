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
        @click="ensureResponseAndUpload"
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
import { en } from 'vuetify/locale';

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


// Handle file selection
function handleFileSelect(files) {
  console.log('File selection event:', files, typeof files);
  
  // Extract the actual file object
  let file = null;
  
  if (Array.isArray(files) && files.length > 0) {
    // v-file-input sometimes passes an array
    file = files[0];
  } else if (files instanceof File) {
    // Direct File object
    file = files;
  } else {
    // No valid file
    preview.value = null;
    return;
  }
  
  // Validate that we have a proper File object
  if (!(file instanceof File)) {
    console.error('Invalid file object:', file);
    preview.value = null;
    return;
  }
  
  console.log('Processing file:', file.name, file.type, file.size);
  
  // Create preview
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.value = e.target.result;
  };
  reader.onerror = (e) => {
    console.error('FileReader error:', e);
    errorMessage.value = 'Failed to read file';
  };
  
  reader.readAsDataURL(file);
}


// Add this method before uploadImage()
async function ensureResponseAndUpload() {
  if (!selectedFile.value) return
  
  // Validate file first
  const validation = fileRules[0](selectedFile.value)
  if (validation !== true) {
    errorMessage.value = validation
    return
  }
  
  uploading.value = true
  errorMessage.value = null
  
  try {
    // 1. Ensure response exists by directly calling ensureResponseExists
    await responseStore.ensureResponseExists()
    
    // 2. Check if we have a response URL now
    if (!responseStore.responseUrl) {
      throw new Error('Failed to create response - no response URL available')
    }
    
    console.log('Response exists, URL:', responseStore.responseUrl)
    
    // 3. Now proceed with the upload
    await uploadImage()
    
  } catch (error) {
    console.error('Upload preparation failed:', error)
    errorMessage.value = error.message || 'Failed to prepare upload. Please try again.'
    uploading.value = false
  }
}


// Upload image to the server
async function uploadImage() {
  try {
    console.log('Question object:', props.question);
    console.log('Answer object:', props.answer);
    
    // Create FormData for the upload
    const formData = new FormData()
    formData.append('question', props.question.url)
    formData.append('image', selectedFile.value)
    formData.append('response', responseStore.responseUrl)
    
    // Handle mapview - only append if it exists and is valid
    const mapviewUrl = props.answer?.mapview?.url || props.question?.mapview;
    if (mapviewUrl && mapviewUrl.trim() !== '' && mapviewUrl !== 'null') {
      console.log('Adding mapview to form:', mapviewUrl);
      formData.append('mapview', mapviewUrl);
    } else {
      console.log('No mapview provided - field will be null');
    }

    console.log('responseurl', responseStore.responseUrl)
    
    // Make API call to upload image
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