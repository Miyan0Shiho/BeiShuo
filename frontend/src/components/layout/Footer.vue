<script setup>
// 页脚组件
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="bg-dark text-white pt-16 pb-8">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid md:grid-cols-4 gap-8 mb-12">
        <!-- 关于我们 -->
        <div>
          <div class="flex items-center mb-4">
            <i class="fas fa-monument text-accent text-2xl mr-2"></i>
            <span class="text-xl font-serif font-bold">碑说</span>
          </div>
          <p class="text-white/60 mb-4">
            碑说致力于通过AI技术，让古老碑文焕发新生，为历史文化传承贡献力量。
          </p>
          <div class="flex space-x-4">
            <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
              <i class="fab fa-weibo"></i>
            </a>
            <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
              <i class="fab fa-weixin"></i>
            </a>
            <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
              <i class="fab fa-qq"></i>
            </a>
            <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
              <i class="fab fa-github"></i>
            </a>
          </div>
        </div>

        <!-- 快速链接 -->
        <div>
          <h4 class="text-lg font-semibold mb-4">快速链接</h4>
          <ul class="space-y-2">
            <li>
              <router-link to="/" class="text-white/60 hover:text-accent transition-custom">
                首页
              </router-link>
            </li>
            <li>
              <router-link to="/recognition" class="text-white/60 hover:text-accent transition-custom">
                碑文识别
              </router-link>
            </li>
            <!-- <li>
              <router-link to="/history" class="text-white/60 hover:text-accent transition-custom">
                历史记录
              </router-link>
            </li> -->
            <li>
              <router-link to="/knowledge" class="text-white/60 hover:text-accent transition-custom">
                碑文知识库
              </router-link>
            </li>
            <li>
              <router-link to="/favorites" class="text-white/60 hover:text-accent transition-custom">
                我的碑文
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 帮助中心 -->
        <div>
          <h4 class="text-lg font-semibold mb-4">帮助中心</h4>
          <ul class="space-y-2">
            <li>
              <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
                使用教程
              </a>
            </li>
            <li>
              <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
                常见问题
              </a>
            </li>
            <li>
              <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
                联系我们
              </a>
            </li>
            <li>
              <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
                意见反馈
              </a>
            </li>
            <li>
              <a href="javascript:void(0)" class="text-white/60 hover:text-accent transition-custom">
                技术支持
              </a>
            </li>
          </ul>
        </div>

        <!-- 联系我们 -->
        <div>
          <h4 class="text-lg font-semibold mb-4">联系我们</h4>
          <ul class="space-y-3">
            <li class="flex items-start">
              <i class="fas fa-map-marker-alt text-accent mt-1 mr-3"></i>
              <span class="text-white/60">北京市海淀区中关村南大街5号</span>
            </li>
            <li class="flex items-center">
              <i class="fas fa-phone text-accent mr-3"></i>
              <span class="text-white/60">400-123-4567</span>
            </li>
            <li class="flex items-center">
              <i class="fas fa-envelope text-accent mr-3"></i>
              <span class="text-white/60">contact@beishuo.com</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- 版权信息 -->
      <div class="border-t border-white/10 pt-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-white/40 text-sm mb-4 md:mb-0">
            © {{ currentYear }} 碑说 AI 碑文识别与阐释平台. 保留所有权利.
          </p>
          <div class="flex space-x-6">
            <a href="javascript:void(0)" class="text-white/40 hover:text-white/70 text-sm transition-custom">
              隐私政策
            </a>
            <a href="javascript:void(0)" class="text-white/40 hover:text-white/70 text-sm transition-custom">
              服务条款
            </a>
            <a href="javascript:void(0)" class="text-white/40 hover:text-white/70 text-sm transition-custom">
              Cookie政策
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
/* 页脚样式 */
</style>
