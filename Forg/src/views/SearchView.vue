<script setup lang="ts">
import ResultComponent from '@/components/ResultComponent.vue';
import SearchBarComponent from '@/components/SearchBarComponent.vue';
import { provide } from 'vue';
import { ref } from 'vue';
import { onMounted } from 'vue';
import { reactive } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute()

const searchTerms = ref(route.params.searchTerm)

const data = reactive({records:{
  page:0,
  page_size:0,
  pages:0,
  results:[],
  total: 0
}}) 

const fetchData = async()=>{
  let response = await fetch("http://localhost:5000/search?q="+searchTerms.value);
  let fetchedRecords = await response.json();
  data.records = fetchedRecords;
}

function search(val){
  searchTerms.value = val
  fetchData()
}

provide('search', search)

onMounted(()=>fetchData())
</script>

<template>
  <div>
    <SearchBarComponent/>
    <br>
    <ResultComponent class="ml-4 mr-4" v-for="record in data.records.results" :data="record"/>
    <br><br>
  </div>
</template>

<style>
</style>
