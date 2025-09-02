<template>
  <v-container style="padding: 16px">

    <!-- Likert scale radio buttons -->
    <div class="likert-scale">
      <v-radio-group
        v-model="selectedValue"
        @update:model-value="updateAnswer"
        row
        class="likert-radio-group"
        :mandatory="question?.required"
      >
        <div class="likert-options">
          <div 
            v-for="point in scalePoints" 
            :key="point"
            class="likert-option"
          >
            <v-radio 
              :value="point.toString()"
              class="likert-radio"
            />
            <div class="likert-label text-caption text-center">
              {{ likertConfig?.labels?.[point.toString()] || `Point ${point}` }}
            </div>
          </div>
        </div>
      </v-radio-group>
    </div>

    <!-- Selected value display -->
    <div v-if="selectedValue" class="selected-display mt-3">
      <v-chip color="primary" size="small" variant="flat">
        {{ likertConfig?.labels?.[selectedValue] || 'Unknown' }}
      </v-chip>
    </div>
  </v-container>
</template>

<script>
export default {
  name: "AnswerTypeLikertScale",
}
</script>

<script setup>
import { errorMessages } from 'vue/compiler-sfc';

const emit = defineEmits(['updateAnswer'])
const props = defineProps({
  question_index: Number,
  question: Object,
  answer: Object,
})

// Reactive data
const selectedValue = ref(props.answer?.text || '')

// Computed properties
const likertConfig = computed(() => {
  const config = props.question?.likert_config
  if (!config) {
    // Default 5-point satisfaction scale

    errorMessages('No likert_config found on question')
  }
  
  return config
})

console.log('likertConfig', likertConfig.value)

const scalePoints = computed(() => {
  const points = likertConfig.value?.scale_points || 5
  return Array.from({ length: points }, (_, i) => i + 1)
})

// Methods
function updateAnswer(value) {
  selectedValue.value = value
  
  // Set the answer text to include only the value
  const label = likertConfig.value?.labels?.[value] || 'Unknown'
  props.answer.text = `${value}`
  
  // Emit the update following the maptool pattern
  emit('updateAnswer', props.answer, props.question_index)
}

// Watch for changes in answer prop (for initialization)
watch(() => props.answer?.text, (newValue) => {
  if (newValue && newValue !== selectedValue.value) {
    // Extract just the numeric value if the text contains "value - label" format
    const match = newValue.match(/^(\d+)/)
    if (match) {
      selectedValue.value = match[1]
    } else {
      selectedValue.value = newValue
    }
  }
}, { immediate: true })

// Initialize component
onMounted(() => {
  if (props.answer?.text) {
    // Extract numeric value from existing answer if it exists
    const match = props.answer.text.match(/^(\d+)/)
    if (match) {
      selectedValue.value = match[1]
    } else {
      selectedValue.value = props.answer.text
    }
  }
})
</script>

<style scoped>
.scale-anchors {
  margin-bottom: 16px;
}

.likert-scale {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px 16px;
  margin: 16px 0;
}

/* Force horizontal layout for radio group */
.likert-radio-group :deep(.v-selection-control-group) {
  flex-direction: row !important;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  gap: 8px;
}

.likert-options {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  gap: 8px;
}

.likert-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 0;
}

/* Radio button styling */
.likert-radio {
  margin-bottom: 8px;
}

.likert-radio :deep(.v-selection-control) {
  min-height: auto;
  align-items: center;
  justify-content: center;
}

/* Label styling */
.likert-label {
  max-width: 100%;
  word-wrap: break-word;
  text-align: center;
  line-height: 1.3;
  font-size: 0.75rem;
  color: #666;
  hyphens: auto;
}

.selected-display {
  text-align: center;
}

/* Responsive design */
@media (max-width: 768px) {
  .likert-scale {
    padding: 16px 8px;
  }
  
  .likert-options {
    gap: 4px;
  }
  
  .likert-label {
    font-size: 0.7rem;
    line-height: 1.2;
  }
}

@media (max-width: 600px) {
  .likert-options {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  
  .likert-option {
    flex-direction: row;
    justify-content: flex-start;
    width: 100%;
    max-width: 300px;
  }
  
  .likert-label {
    margin-left: 12px;
    text-align: left;
    max-width: none;
    font-size: 0.875rem;
  }
}
</style>
