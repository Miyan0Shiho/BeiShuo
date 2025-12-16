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
    {
      path: "/imports",
      name: "Imports",
      component: () => import("../views/Imports.vue"),
      meta: { title: "我的导入 - 碑说", requiresAuth: true },
    },
    {
      path: "/my-inscriptions/:id",
      name: "MyInscriptionDetail",
      component: () => import("../views/MyInscriptionDetail.vue"),
      meta: { title: "我的碑文详情 - 碑说" },
    },
    {
      path: "/my-imports/:id",
      name: "ImportDetail",
      component: () => import("../views/ImportDetail.vue"),
      meta: { title: "我的导入详情 - 碑说", requiresAuth: true },
    },
  ],
});

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  try {
    const token = localStorage.getItem('token')
    if (to.meta.requiresAuth && !token) {
      next('/favorites')
      return
    }
  } catch {}
  next();
});

export default router;
