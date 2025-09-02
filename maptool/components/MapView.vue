
<template>
    <v-sheet width="auto">
        <!-- <template v-slot:activator="{ props }">
            <v-btn class="mt-4" variant="tonal" append-icon="mdi-pencil" border v-bind="props">Edit Map</v-btn>
        </template> -->
        <v-card>
            <v-card-text>
                <!-- <v-text-field v-model="title" label="Name of map view" variant="outlined"></v-text-field> -->
                <!-- <p>Map name: {{ questionMapView.name }}</p> -->
                <div style="height:600px; width:auto">
                    <l-map ref="mapGeometriesRef" 
                        :zoom="questionMapView.options.zoom" 
                        :center="questionMapView.options.center"
                        @ready="onMapWWControlReady"  @update:zoom="handleUpdateMapViewZoom"
                        @update:center="handleUpdateMapViewCenter" :noBlockingAnimations="true">
                        <l-tile-layer 
                            :url="questionMapView.map_service_url"
                            layer-type="base"
                            >
                        </l-tile-layer>
                        <l-geo-json 
                        @ready="geoJsonReady" :key="updateKeyGeoJson">
                        </l-geo-json>
                        <l-feature-group ref="featureGroupRef">

                        </l-feature-group>
                    </l-map>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-btn variant="tonal" color="primary" block @click="submitMap">Save map</v-btn>
                <!-- <v-btn color="primary" block @click="dialog = false">Save</v-btn> -->
            </v-card-actions>
        </v-card>
    </v-sheet>
</template>
  
<script setup>
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-toolbar/dist/leaflet.toolbar.css";
import { LMap, LTileLayer, LFeatureGroup, LGeoJson, LCircle, LCircleMarker } from "@vue-leaflet/vue-leaflet";
import "leaflet-draw/dist/leaflet.draw-src.js";
import "leaflet-toolbar";
import "leaflet-draw-toolbar/dist/leaflet.draw-toolbar.js";
import { ref, reactive, onMounted, onBeforeMount } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { forEach } from 'ramda'
// Store

import { useAnswerMapViewStore } from "~/stores/answerMapview";
import { useResponseStore } from "~/stores/response";
import { useQuestionDesignStore } from "~/stores/questionDesign";
import { useGlobalStore } from '~/stores/global';
import { parse } from "postcss";
import { th } from "vuetify/locale";

// API endpoints
const map_views_endpoint = '/map-views/'

const questionStore = useQuestionDesignStore()

const answerMapViewStore = useAnswerMapViewStore()
const responseStore = useResponseStore()
answerMapViewStore.$reset()

const props = defineProps({
    mapViewUrl: String | undefined
})


function extractMapviewId(mapUrl) {
    /*
    * Extracts the mapview id from the url
    * @param {String} mapViewUrl 
    * @returns {Number} id
    */
    const match = mapUrl.match(/\d+\/?$/);
    if (match) {
        const id = parseInt(match[0], 10);
        return id;
    } else {
        throw new Error('Could not extract mapview id from url', mapUrl)
    }
}

const route = useRoute();
var question_id = route.params.question; // use url questions id as an index to load each question 
let answer_index = question_id -1;  // gets the id for the questions

var questionMapView;
// console.log('props.mapViewUrl //> ', props.mapViewUrl)
// Fetch the map view for corresponding Question
if (props.mapViewUrl) {
    const mapViewId = extractMapviewId(props.mapViewUrl)
    // console.log('mapViewId //> ', mapViewId)
    const {data, error, pending} = await useCmsApiData(`${map_views_endpoint}${mapViewId}`)
    
    // console.log('mapview data', data.value)

    questionMapView = data.value
    // store the mapview values to answerMapViewStore
    answerMapViewStore.updateMapServiceUrl(questionMapView.map_service_url)
    answerMapViewStore.updateZoomLevel(questionMapView.options.zoom)
    answerMapViewStore.updateCenter(questionMapView.options.center)
    if (error?.value) {
        throw new Error('error in questionMapView //> ', error)
    }
}


const mapGeometriesRef = ref() 
// Map without controls
const storedMapWithoutControls = ref(null)
// Map with controls (the pop up one)
const mapRef = ref(null)
const featureGroupRef = ref(null)
const featureGroupRefWControl = ref(null)
// const dialog = ref(props.dialogOpen)
const drawnItemsRef = ref(null)

const optionsTempStoreZoom = ref(null)
const optionsTempStoreCenter = ref(null)
const updateKeyMapWithoutControls = ref(0)
const updateKeyGeoJson = ref(0)


// collects map parameters for the user's answer
const currentMapView = reactive({
    map_service_url: null,
    options: { 
        zoom:  null,
        center:  [] },
    name: "", 
    geometries: {
        type: "FeatureCollection",
        features: []
    }
});

const handleUpdateMapViewZoom = (updatedZoom) => {
    // Handle the updated answer here
    currentMapView.options.zoom = updatedZoom;
    answerMapViewStore.updateZoomLevel(updatedZoom);
};

const handleUpdateMapViewCenter = (updatedCenter) => {
    // Update the center of the map. Converts object {lat:value, lng:value} to array [lat, lng]
    // console.log('current mapview \\>', currentMapView);
    const newCenter = [updatedCenter.lat, updatedCenter.lng];
    currentMapView.options.center = newCenter;
    answerMapViewStore.updateCenter(newCenter);
};


const mapViewAnswerData = reactive({
    id: props.mapViewId || null,
    url: props.mapViewUrl || null,
    options: { zoom: 8, center: [52.045, 5.10] },
    name: "", 
    geometries: {
        type: "FeatureCollection",
        features: []
    }
})


/**
 * Utils
 */
const setGeoJsonMarkers = () => {
    // const drawnItems = featureGroupRef.value.features // this schould be a leafleft object?
    const drawnItems = featureGroupRef.value.leafletObject
    const initialGeojson = mapViewAnswerData.geometries;

    initialGeojson.features.forEach((feature) => {
        const layer = L.geoJSON(feature, {
            pointToLayer: function (feature, latlng) {
                if (feature.properties.radius) {
                    return L.circle(latlng, { radius: feature.properties.radius });
                } else {
                    return L.marker(latlng);
                }
            },
        }).addTo(drawnItems);
        // console.log('drawnItems //> ', drawnItems)
        drawnItems.addLayer(layer);
    });
}

/**
 * Listeners
 */

const geoJsonReady = () => {
    setGeoJsonMarkers()
};


/**
 * Computed functions
 */

const title = computed({
    get: () => props.title || mapViewAnswerData.name,
    set: (value) => {
        mapViewAnswerData.name = value
    }
})

/**
 * Methods
 */

 const emit = defineEmits(['saveDescription']);

 const handleSaveDescription = (description) => {
      // Emit the saveDescription event with the description text
      emit('saveDescription', description);
    //   console.log('Description saved:', description);
      // You can also perform other actions here, like sending the description to a server
      // TODO: Fix. save the description to the layer
    }


/**
 * Add the props.geojson to the drawnItemsRef value
 */


const onMapWWControlReady = () => {
    const map = mapGeometriesRef.value.leafletObject;
    if (map !== null) {
        drawnItemsRef.value = featureGroupRef.value.leafletObject;

        if (currentMapView.geometries?.features) {
            const drawnItems = drawnItemsRef.value; // TODO: check if this is the correct way to hangle geometries during map load
            const initialGeojson = currentMapView.geometries;

            initialGeojson.features.forEach((feature) => {
                const layer = L.geoJSON(feature, {
                    pointToLayer: function (feature, latlng) {
                        if (feature.properties.radius) {
                            return L.circle(latlng, { radius: feature.properties.radius });
                        } else {
                            return L.marker(latlng);
                        }
                    },
                }).addTo(drawnItems);
                drawnItems.addLayer(layer);
            });
        }

        // Initialize the draw control and pass it the FeatureGroup of editable layers
        const drawControl = new L.Control.Draw({
            edit: {
                featureGroup: drawnItemsRef.value,
            },
            draw: {
                circle: true, // Add circle shape
                marker: true,
                polyline: true,
                polygon: true,
                rectangle: false,
                circleMarker: false,
            }
        });

        map.addControl(drawControl);
        // set options
        // map.setView(mapViewData.options.center, mapViewData.options.zoom);

        map.on(L.Draw.Event.CREATED, (event) => {
            const layer = event.layer;
            const layerType = event.layerType;

            if (layerType === 'circle') {
                const radius = layer.getRadius();
                const latlng = layer.getLatLng();
                const geojsonFeature = {
                    type: 'Feature',
                    properties: { radius: radius },
                    geometry: { type: 'Point', coordinates: [latlng.lng, latlng.lat] },
                };
                const circleLayer = L.geoJSON(geojsonFeature, {
                    pointToLayer: function (feature, latlng) {
                        return L.circle(latlng, { radius: feature.properties.radius });
                    },
                });
                drawnItemsRef.value.addLayer(circleLayer);
            } else {                
                drawnItemsRef.value.addLayer(layer); 
            }
            // popup
            const popupContent = document.createElement('div');
            popupContent.style.width = '200px'; // Set the width of the popup
            const input = document.createElement('input');
            input.type = 'text';
            input.id = 'feature-description';
            input.placeholder = 'Type a description';
            input.style.width = '100%'; // Make input take the full width of its parent
            input.style.padding = '5px 5px'; 
            input.style.borderRadius = '3px'; 
            input.style.overflowWrap = 'break-word'; // Break long words to prevent overflow
            
            const saveButton = document.createElement('button');
            saveButton.textContent = 'Save';
            saveButton.style.backgroundColor = '#FF4C50';
            saveButton.style.color = 'white'; 
            saveButton.style.padding = '4px 8px'; 
            saveButton.style.borderRadius = '5px'; 
            saveButton.style.marginTop = '10px'; 
            saveButton.onclick = () => {
                // console.log('layer value //> ', input.value)
                handleSaveDescription(input.value);
                // TODO: check if options are saved to the map view
                // event.layer.properties.description = input.value;    
                // drawnItemsRef.value.addLayer(event.layer);

                // console.log('drawItems ref //> ', drawnItemsRef.value);
                // event.layer.bindPopup(input.value, closeButton = true);
                // console.log('event layer  //> ', event.layer);
                // TODO: Fix. save the description to the layer

                // layer.properties = { description: input.value };
            };

            popupContent.appendChild(input);
            popupContent.appendChild(saveButton);

            layer.bindPopup(popupContent);
            
                    //   
            
            // console.log('drawnItemsRef.value  add //> ', drawnItemsRef.value.toGeoJSON())

            answerMapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });

        map.on(L.Draw.Event.DELETED, (event) => {
            const layers = event.layers;
    
            layers.eachLayer((layer) => {
                // console.log('layer to remove //> ', layer)
                    drawnItemsRef.value.removeLayer(layer);
            });
            // console.log('drawnItemsRef.value  delete //> ', drawnItemsRef.value.toGeoJSON())
            answerMapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });

        map.on(L.Draw.Event.EDITED, (event) => {
            const layers = event.layers;
            layers.eachLayer((layer) => {
                // Remove the old version of the edited layer
                drawnItemsRef.value.removeLayer(layer);
                // Add the updated version of the edited layer
                drawnItemsRef.value.addLayer(layer);
            });
            answerMapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });
    }
};


const current_question_id = route.params.question
const suveryStore = useSurveyStore()
const current_question_url = suveryStore.questions[current_question_id-1].url

// CONTINUE HERE
/// TODO: check why a new answer is created in response store when  text is updated, after map is saved


const submitMap = async () => {
    // const global = useGlobalStore()
    let response
    // mapViewAnswerData.geometries = drawnItemsRef.value.toGeoJSON()

    /**
     * Check if the mapView already exists, if it exist then update, if not then create a new one
     */
    
    if (answerMapViewStore.name === null) {
        answerMapViewStore.updateName(uuidv4())
    };

    if (answerMapViewStore.url) {
        const mapview_slug = answerMapViewStore.url.match(/map-views\/.*/);
        response = await answerMapViewStore.updateMapview(mapview_slug)

        

    } else {
        // mapViewAnswerData.name = mapViewAnswerData?.name || uuidv4()
        response = await answerMapViewStore.createMapview()
        if (response.data) {
            // responseStore.updateAnswerMapView
            // responseStore.answers.push(answer);
            const answer_mapview = {
                question_url: current_question_url, 
                mapview: {
                    url: answerMapViewStore.url,
                    location: answerMapViewStore.location
                } }
            responseStore.updateAnswerMapView(answer_mapview)
            // console.log('response.data //> ', response.data)
            // console.log('mapstore answer //> ', answer_mapview)
        }

        // responseStore.updateAnswerMapView(answer_index, mapViewStore.getMapViewAnswer)
    }


    // TODO: find a solution to update the anwer object in response store when map is saved for
    // the first time. But not modify the answer object when the map is updated.
   
    // if (response.data) {
    //     mapViewData.name = response.data.name
    //     await questionStore.editCurrentQuestionKeyValue(props.questionIndex, { map_view: response.data.id })
    //     await questionStore.saveCurrentQuestions()
    // }
    updateKeyMapWithoutControls.value++
    setGeoJsonMarkers()
    // response.refresh()
    // global.succes('Map view saved')
    
}


</script>
  
<style></style>