import path from "path"
// https://v3.nuxtjs.org/api/configuration/nuxt.config
import vuetify from "vite-plugin-vuetify";
import pinia from '@pinia/nuxt';

const ONE_DAY = 60 * 60 * 24 * 1000
const ONE_WEEK = ONE_DAY * 7



export default defineNuxtConfig({

  ssr: true,

  build: {
      transpile: ["vuetify", "vue-toastification/nuxt"],
  },

  // For speeding up load time in development, loading in all components from external packages increases the loading time, here we disabling to auto imports
  components: {
      dirs: [
          '~/components'
      ]
  },

  experimental: {
      inlineSSRStyles: false
  },

  nitro: {
      compressPublicAssets: true,
},

  app: {
      baseURL: '/citizen-map/',
      head: {
          title: "Citizen Mapping Tool",
          link: [
              { rel: 'icon', type: 'image/x-icon', href: '/favicon-blue.png' },
              {
                  rel: 'stylesheet', href: 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css',
                  integrity: 'sha256-kLaT2GOSpHechhsozzB+flnD+zUyjE2LlfWPgU04xyI=', crossorigin: ''
              },
          ],
          script: [
              {
                  src: "https://unpkg.com/leaflet@1.9.3/dist/leaflet.js",
                  integrity: "sha256-WBkoXOwTeyKclOHuWtc+i2uENFpDZ9YPdf5Hf+D7ewM=",
                  crossorigin: ""
              }
          ]
      }
  },

  css: [
      '@mdi/font/css/materialdesignicons.min.css',
  ],

  imports: {
      dirs: [
          'stores',
          // Scan top-level modules      
          'composables',
          // ... or scan modules nested one level deep with a specific name and file extension      
          'composables/*/index.{ts,js,mjs,mts}',
          // ... or scan all modules within given directory      
          'composables/**'
      ]
  },

  plugins: [
      //     { src: '@/plugins/vuedraggable' }
      // { src: '@/plugins/vue-draggable/index.js', ssr: false }
  ],

  vite: {
      define: {
          'process.env.DEBUG': false,
      },
      ssr: {
          noExternal: ["vuetify"],
      },
      
  },

  modules: [
      // We are using @pinia/nuxt for the store
      pinia,

      // Nuxt api party is used for the proxy API
      'nuxt-api-party',

      // We are not using this now but maybe in the future
      // '@kevinmarrec/nuxt-pwa',

      // We are using tailwind utility classes instead of the Vuetify utility css classes
      // More info: https://tailwindcss.nuxtjs.org/
      '@nuxtjs/tailwindcss',
      
      // We are using NuxtOpenFetch for OpenAPI clients
      // More info: https://nuxt-open-fetch.vercel.app/setup/quick-start
 

      // this adds the vuetify vite plugin
      // also produces type errors in the current beta release
      async (options, nuxt) => {
          nuxt.hooks.hook("vite:extendConfig", (config) => config.plugins.push(vuetify()));
      },
  ],
  
  tailwindcss: {
    exposeConfig: true,
    viewer: true,
    // and more...
  },

  runtimeConfig: {
    cookieName: process.env.COOKIE_NAME || '__session',
    cookieSecret: process.env.COOKIE_SECRET || 'secret',
    cookieExpires: parseInt(process.env.COOKIE_REMEMBER_ME_EXPIRES || ONE_DAY.toString(), 10), // 1 day
    cookieRememberMeExpires: parseInt(process.env.COOKIE_REMEMBER_ME_EXPIRES || ONE_WEEK.toString(), 10), // 7 days
    public: {
        // set api for reference to the frontend
        // usage: `${config.public.apiBaseAPI}`
    //   apiBaseCms: "/api/v2", 
        apiHostPayment: '',
    //   apiBaseAuth: "/api/auth"
    },

    // API party configuration
    apiParty: {
        endpoints: {
            cmsApi: { // Becomes `$cmsApi()` and useCmsApiData()
                url: process.env.API_PARTY_CMS_URL || 'http://localhost:8000/voice/v3',
                // token: '',
                schema: './openapi/voice/openapi.yml',
                // allowedUrls: [ ],
            },
            authApi: { // Becomes `$authApi()` and useAuthApiData()
                url: process.env.AUTH_API_URL || 'http://localhost:8000/_allauth/browser/v1/auth',
                schema: './openapi/voice/openapi.yml'
            }
        }
    },
      paymentSecretKey: '',
  },

  hooks: {
    //   'pages:extend'(routes) {
    //       routes.push({
    //           name: "survey-design",
    //           path: "/design/surveys/create",
    //           file: path.resolve(__dirname, './pages/design/surveys/[_id]/index.vue')
    //       });
    //       return routes
    //   }
  },

  routeRules: {
      // Render these routes with SPA // See: https://nuxt.com/docs/guide/concepts/rendering#route-rules
      '/design/**': { ssr: false },
      '/design/surveys/**': { ssr: false },
      '/user/**': { ssr: false },
      '/surveys/**': { ssr: false },
  },

  compatibilityDate: '2025-03-03',
});

