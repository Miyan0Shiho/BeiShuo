import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, from, savedPosition) {
    // 始终滚动到页面顶部
    return { top: 0 }
  },
  routes: [
    {
      path: "/",
      name: "Home",
      component: () => import("../views/Home.vue"),
      meta: { title: "首页 - 碑说" },
    },
    {
      path: "/recognition",
      name: "Recognition",
      component: () => import("../views/Recognition.vue"),
      meta: { title: "碑文识别 - 碑说" },
    },
    // {
    //   path: '/history',
    //   name: 'History',
    //   component: () => import('../views/History.vue'),
    //   meta: { title: '历史记录 - 碑说' }
    // },
    {
      path: "/knowledge",
      name: "Knowledge",
      component: () => import("../views/Knowledge.vue"),
      meta: { title: "碑文知识库 - 碑说" },
    },
    {
      path: "/knowledge/article/:id",
      name: "Article",
      component: () => import("../views/Article.vue"),
      meta: { title: "文章详情 - 碑说" },
    },
    {
      path: "/favorites",
      name: "Favorites",
      component: () => import("../views/Favorites.vue"),
      meta: { title: "我的碑文 - 碑说" },
    },
  ],
});

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  next();
});

export default router;
