<template>
  <v-app id="inspire">
    <v-app-bar
            app
            color="indigo"
            dark
    >

        <v-toolbar-title>
          <router-link to="/" style="color : #ffffff; text-decoration: none;"> Python Url Analysis </router-link>
        </v-toolbar-title>

    </v-app-bar>

    <v-content>
      <router-view/>
    </v-content>
  </v-app>
</template>

<script>
  export default {
    data: function(){
      return{
      }
    }
  }
</script>

