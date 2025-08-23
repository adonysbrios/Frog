<template>
  <form
    v-if="props.size == 'x'"
    v-on:submit.prevent="eventSubmit"
    class="flex justify-center"
  >
    <input
      v-model="searchTerm"
      placeholder="Search ..."
      required
      class="px-4 text-base-content/70 text-[1rem] py-2 border-solid border-base-300 bg-base-200 w-[500px] min-w-[100px] max-w-[500px] rounded-r-none border-2 rounded-full"
      type="text"
    />
    <button
      class="px-4 text-base-content/70 text-[20px] py-2 border-solid border-base-300 bg-base-200 rounded-l-none border-2 rounded-full"
    >
      <searchicon width="27" height="27" />
    </button>
  </form>
  <form v-else v-on:submit.prevent="eventSubmit" class="flex justify-center">
    <input
      v-model="searchTerm"
      placeholder="Search ..."
      required
      class="px-4 text-[13px] text-base-content/70 py-1 border-solid border-base-300 bg-base-200 flex max-w-[300px] rounded-r-none border-2 rounded-md"
      type="text"
    />
    <button
      class="px-4 text-base-content/70 text-s py-1 border-solid border-base-300 bg-base-200 rounded-l-none border-2 rounded-md"
    >
      <searchicon width="20" height="20" />
    </button>
  </form>
</template>

<script setup>
import searchicon from "@/components/icons/Search.vue";
import { inject } from "vue";
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const props = defineProps(["size"]);
const searchTerm = ref();

let search = inject("search");

const eventSubmit = (e) => {
  router.push({ name: "search", params: { searchTerm: searchTerm.value } });
  if (search) {
    search(searchTerm.value);
  }
};
</script>
