/**
 * This to store the mapview data of an Answer in a Response
 * 
 */

import { defineStore, } from 'pinia'
import setRequestConfig from './utils/setRequestConfig';
import { useGlobalStore } from './global'
import { da, el, th } from 'vuetify/locale';


export const useAnswerMapViewStore = defineStore('answerMapView', {
    state: () => ({
        id: null,
        url: null,
        name: null,
        description: '',
        location: null,
        mapServiceUrl: null,
        zoomLevel: null,
        center: null,
        geometries: {} // a GeoJSON featurecollection for all geometries
    }),
    getters: {
        // getCurrentQuestions: (state) => state.currentQuestions
        getGeometries: (state) => state.geometries,
        getZoomLevel: (state) => state.zoomLevel,
        getCenter: (state) => state.center,
        getMapServiceUrl: (state) => state.mapServiceUrl,
        getMapViewAnswer: (state) => {
            return {
                url: state.url,
                location: state.location
        }}
    },
    actions: {
        updateGeometries(geometries) {
            this.geometries = geometries
        },
        updateZoomLevel(zoomLevel) {
            this.zoomLevel = zoomLevel
        },
        updateCenter(center) {
            this.center = center
        },
        updateMapServiceUrl(mapServiceUrl) {
            this.mapServiceUrl = mapServiceUrl
        },
        updateName(name) {
            this.name = name
        },
        updateLocation(location) {
            this.location = location
        },
        async createLocations(){
            /**
             * Creates locations using the geometries in state.geometries
             * 
             * returns new state of location.
             */
            // create the location collection, if there are geometries
            if (Object.keys(this.geometries).length !== 0) {
                const {data, error, pending } = await useAsyncData( () => $cmsApi(`/locations/`, 
                    { method: 'POST', 
                      headers: {'Content-Type': 'application/json'},
                      body: {
                        name: this.name, 
                        description: this.description,
                    } 
                    }
                ));

                if (data.value) {
                    this.location =  data.value.url
                    // console.log('location_url //> ', data)
                } 

                if (error.value) {
                    throw new Error('Error creating location collection //> ', error.value)
                }
                
                // Create the geometries and add them to the location collection
                this.geometries.features.forEach( async (feature) => {

                    var feature_endpoint;
                    if (feature.geometry.type === "Point"){
                        feature_endpoint = `/pointfeatures/`;    
                    } else if (feature.geometry.type === "LineString") {
                        feature_endpoint = `/linefeatures/`;    
                    } else if (feature.geometry.type === "Polygon") {
                        feature_endpoint = `/polygonfeatures/`
                    } else {
                        throw new Error('Unsupported geometry type //> ', feature.geometry.type)
                    }

                    const {data, error, pending } = await useAsyncData( () => $cmsApi(feature_endpoint, 
                        { method: 'POST', 
                          headers: {'Content-Type': 'application/json'}, 
                          body: {
                            geom: feature.geometry,
                            description: 'created from mapview store',
                            location: this.location
                        } 
                        }
                    ));

                    if (error.value) {
                        throw new Error('Error creating feature //> ', error.value)
                    }
                })

            } else {
                this.location = null
            };
            return this.location

        },
        async updateLocations(){
            /**
             * Updates locations using the geometries in state.geometries
             * 
             * returns new state of location.
             */
            // create the location collection, if there are geometries

            this.geometries.features.forEach( async (feature) => {

                var feature_endpoint;
                if (feature.geometry.type === "Point"){
                    feature_endpoint = `/pointfeatures/`;    
                } else if (feature.geometry.type === "LineString") {
                    feature_endpoint = `/linefeatures/`;    
                } else if (feature.geometry.type === "Polygon") {
                    feature_endpoint = `/polygonfeatures/`
                } else {
                    throw new Error('Unsupported geometry type //> ', feature.geometry.type)
                }

                const {data, error, pending } = await useAsyncData( () => $cmsApi(feature_endpoint, 
                    { method: 'PUT', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: {
                        geom: feature.geometry,
                        annotation: 'created from mapview store',
                        location: this.location
                    } 
                    }
                ));

                if (error.value) {
                    throw new Error('Error creating feature //> ', error.value)
                }
            })

            return this.location
        },

        async createMapview() {
            /**
             * Create a new mapview in the backend with the current state of the store
             */
            // const csrftoken = user.getCookie('csrftoken');
            // var location_url;
            
            const location_url = await this.createLocations();
    
            const config = setRequestConfig({ method: 'POST', headers:{
                'Content-Type': 'application/json'
             }, body: {
                name: this.name,
                map_service_url: this.mapServiceUrl,
                options: {
                    zoom: this.zoomLevel,
                    center: this.center
                },
                location: location_url
             } 
            })

            const global = useGlobalStore()
            // const config = setRequestConfig({ method: 'POST', body: this.getFormattedBody })
            const { data, error, refresh } = await useAsyncData(() => $cmsApi(`/map-views/`, config));

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error.value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                return null
            }

            if (data.value) {
                this.id = data.value.id
                this.url = data.value.url               
            }

            // Notification
            global.succes('Map saved')
            return { data: data?.value, refresh }
        },
        async updateMapview(mapview_url) {
            const global = useGlobalStore()
            // console.log('mapview url at store //> ', mapview_url)
            const config = setRequestConfig({ method: 'PATCH', 
                body: {
                    name: this.name,
                    map_service_url: this.mapServiceUrl,
                    options: {
                        zoom: this.zoomLevel,
                        center: this.center
                    },
                    location: this.location,
                 } 
             })

            // CONTINUE HERE, approach the issue of updating the location starting from here the updateMapview (below). Update the mapview instead of updating the location if possible.
             // TODO: modify to update locations and geometries
            const { data, error, refresh } = await useAsyncData( () => $cmsApi(`${mapview_url}`, config));

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error.value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                return null

            }
            // Notification
            global.succes('Map has been updated')
            return { data: data?.value, refresh }
        },
        async fetchMapView(url) {
            // console.log('Map_view id //> ', url)
            const config = setRequestConfig({ method: 'GET' })
            const {data: res, error } = await useAsyncData( () => $cmsApi(`${url}`, config));

            //  console.log('Map_view res //> ', res)
            if (res?.value) {
                this.id = res.value.id;
                this.url= res.value.url;
                this.name = res.value.name;
                this.mapServiceUrl = res.value.map_service_url;
                // console.log('res.value.options.zoom //> ', res.value.options.zoom)
                this.zoomLevel = res.value.options.zoom;
                this.center = res.value.options.center;
                this.geometries = res.value.geometries
            };
            if (error?.value) {
                throw new Error('Error fetching map view //> ', error.value)
            };
            return res
        }
    },

})