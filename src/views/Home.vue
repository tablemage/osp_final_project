<template>
  <v-container fluid>
      <v-toolbar>
          <v-tabs
                  dark
                  background-color="primary"
                  grow
          >
              <v-tab v-on:click="isFile = true">File</v-tab>
              <v-tab v-on:click="isFile = false">URL</v-tab>
          </v-tabs>
      </v-toolbar>

      <v-card v-if="isFile">
          <v-card-title class="headline">파일 추가</v-card-title>
          <v-form @submit.prevent="fileUpload">
              <v-card-text>
                  <v-row>
                      <v-col class="d-flex" cols="18" sm="9" md="4">
                          <input type="file" ref="inputUpload">
                      </v-col>
                  </v-row>

              </v-card-text>
              <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn type="submit">완료</v-btn>
              </v-card-actions>
          </v-form>
      </v-card>

      <v-card v-if="!isFile">
          <v-card-title class="headline">URL</v-card-title>
          <v-form @submit.prevent="urlUpload">
              <v-card-text>
                  <v-row>
                      <v-col class="d-flex" cols="12" sm="6" md="4">
                          <v-text-field v-model="urlName" label="URL" hide-details outlined dense/>
                      </v-col>
                  </v-row>

              </v-card-text>
              <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn type="submit">완료</v-btn>
              </v-card-actions>
          </v-form>
      </v-card>


  </v-container>
</template>


<script>
    // @ is an alias to /src
    import axios from 'axios'

    export default {
        name: 'home',
        data: function(){
            return {
                isFile : true,
                urlName : ''
            }
        },
        methods:{
            fileUpload(){
                if(! confirm('해당 파일을 업로드 하시겟습니까?')) return;

                const formData = new FormData()
                formData.append('userfile',this.$refs.inputUpload.files[0])

                axios.post('/file',formData,{
                    headers : {
                        'Content-Type': 'multipart/form-data',
                    }
                }).then(()=>{
                    alert('입력이 완료되었습니다.')
                    this.$router.push('/transfer/filelist')
                }).catch((error) => {
                    console.log(error)
                });
            },
            urlUpload(){
                if(! confirm('해당 URL을 업로드 하시겟습니까?')) return;
                const formData = new FormData()
                formData.append('urlName',this.urlName)

                axios.post('/url',formData,{
                }).then(()=>{
                    alert('입력이 완료되었습니다.')
                    this.$router.push('/transfer/onlyurl')
                }).catch((error) => {
                    console.log(error)
                });
            }

        }
    }
</script>
