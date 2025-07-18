<script setup lang="ts">
import { useRouter } from 'vue-router';
import SearchComponent from './SearchComponent.vue';
import LogoIcon from './icons/LogoIcon.vue';
import IconMiniComponent from './icons/IconMiniComponent.vue';

const router = useRouter()

const props = defineProps(['searchTerms'])

</script>

<template>
    <div class="navbar bg-base-100 md:px-10 shadow-sm">
        <div class="flex justify-between w-[100%]">
            <IconMiniComponent class="flex h-[30px] md:hidden" v-on:click="router.push({name:'home'})" v-view-transition-name="'logo'"/>
            <LogoIcon class="hidden md:flex h-[50px] w-[100px]" v-on:click="router.push({name:'home'})" v-view-transition-name="'logo'"/>
            <SearchComponent/>
        </div>
</div>
</template>