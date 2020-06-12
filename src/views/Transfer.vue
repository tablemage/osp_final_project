<template>
    <v-container fluid>
        <v-simple-table>
            <thead>
            <tr>
                <th class="text-left">Url</th>
                <th class="text-left">전체 단어수</th>
                <th class="text-left">처리 시간</th>
                <th class="text-left">분석</th>
                <th class="text-left"><v-btn small color="primary"  @click="addDialog.status=true">Url추가</v-btn></th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(item,i) in list" :key="i">
                <td>{{ item.url }}</td>
                <td>전체 단어수</td>
                <td>처리시간</td>
                <td>
                    <v-btn small color="primary"  v-on:click="getwordDialog(item.url)">단어분석</v-btn>

                    <v-btn small v-on:click="getsimDialog(item.url)">유사도분석</v-btn>
                </td>
                <td></td>
            </tr>
            </tbody>
        </v-simple-table>
        <v-dialog v-model="addDialog.status" >
            <v-card>
                <v-card-title class="headline">Url 추가</v-card-title>
                <v-form @submit.prevent="addUrl">
                    <v-card-text>
                        <v-row>
                            <v-col class="d-flex" cols="12" sm="6" md="4">
                                <v-text-field v-model="addDialog.url" label="url" hide-details outlined dense/>
                            </v-col>
                        </v-row>
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn type="submit">완료</v-btn>
                        <v-btn @click="addDialog.status=false">취소</v-btn>
                    </v-card-actions>
                </v-form>
            </v-card>
        </v-dialog>

        <v-dialog v-model="wordDialog.status">
            <v-card>
                <v-card-title class="headline">단어분석</v-card-title>
                <v-card-text>
                    {{wordDialog.data}}
                </v-card-text>
                <v-card-actions>
                    <v-btn @click="wordDialog.status=false">닫기</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <v-dialog v-model="simDialog.status">
            <v-card>
                <v-card-title class="headline">유사도 분석</v-card-title>
                <v-card-text>
                    {{simDialog.data}}
                </v-card-text>
                <v-card-actions>
                    <v-btn @click="simDialog.status=false">닫기</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>
<script>
    import axios from 'axios'
    export default {
        name: 'Transfer',
        data: function() {
            return {
                addDialog : {
                    status : false,
                    url : ''
                },
                wordDialog : {
                    status : false,
                    data : ''
                },
                simDialog : {
                    status : false,
                    data : ''
                },
                list : []
            }
        },
        mounted(){
            if( typeof this.$route.params.url !== 'undefined' && this.$route.params.url) {
                axios
                    .post('/onlyurl')
                    .then((result)=> {
                        this.list = result.data.list
                        console.log(result)
                        console.log(this.list)
                    })
                    .catch((e)=> {
                        console.log(e)
                    })

            }else{
                axios
                    .post('/filelist')
                    .then((result)=> {
                        this.list = result.data.list
                    })
                    .catch((e)=> {
                        console.log(e)
                    })
            }
        },
        methods :{
            addUrl (){
                axios
                    .post('/addurl',{'url' : this.addDialog.url})
                    .then((result)=> {
                        this.list.push(result.data.list)
                    })
                    .catch((e)=> {
                        console.log(e)
                    })
                this.addDialog.status = false;
            },
            getwordDialog(url){
                axios
                    .post('/word',{'url' : url})
                    .then((result)=> {
                        console.log(result)
                        this.wordDialog.data = result.data.list
                    })
                    .catch((e)=> {
                        console.log(e)
                    });
                this.wordDialog.status = true;
            },
            getsimDialog(url){
                axios
                    .post('/sim',{'url' : url})
                    .then((result)=> {
                        this.simDialog.data = result.data.list
                    })
                    .catch((e)=> {
                        console.log(e)
                    });
                this.simDialog.status = true;
            }
        }
    }
</script>

