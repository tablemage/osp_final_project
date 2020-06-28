<template>
    <v-container fluid>
        <v-simple-table>
            <thead>
            <tr>
                <th class="text-left">Url</th>
                <th class="text-center">Status</th>
                <th class="text-left">전체 단어수</th>
                <th class="text-left">처리 시간</th>
                <th class="text-left">분석</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(item,i) in list" :key="i">
                <td>{{ item.url }}</td>
                <td class="text-center">신규</td>
                <td>{{ item.count }}</td>
                <td>{{ item.resTime }}</td>
                <td>
                    <v-btn small color="primary"  v-on:click="getwordDialog(item.url)">단어분석</v-btn>

                    <v-btn small v-if="simCheck" v-on:click="getsimDialog(item.url)">유사도분석</v-btn>
                </td>
            </tr>
            </tbody>
        </v-simple-table>


        <v-dialog v-model="wordDialog.status">
            <v-card>
                <v-card-title class="headline">단어분석</v-card-title>
                <v-card-text>
                    {{list}}
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
                    <v-simple-table>
                        <thead>
                        <tr>
                            <th class="text-left">순위</th>
                            <th class="text-left">URL</th>
                            <th class="text-left">유사도</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="(item,i) in simDialog.data" :key="i">
                            <td>{{ item.index }}</td>
                            <td>{{ item.url}}</td>
                            <td>{{ item.data }}</td>
                        </tr>
                        </tbody>
                    </v-simple-table>
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
                wordDialog : {
                    status : false,
                    data : ''
                },
                simDialog : {
                    status : false,
                    data : ''
                },
                simCheck : false,
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
                        this.simCheck = false
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

