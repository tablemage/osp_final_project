<template>
  <v-app id="inspire">
    <v-app-bar
            app
            color="indigo"
            dark
    >
      <v-toolbar-title>Python Url Analysis</v-toolbar-title>
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

