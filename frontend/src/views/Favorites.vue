<!--
  [MODULE] d4e_我的碑文页面
-->
<template>
  <section class="py-10 md:py-16">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <!-- [MODULE] e5f_我的碑文页面:页面标题 -->
      <div class="mb-8 flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-2xl md:text-3xl font-serif font-bold text-primary"> 我的碑文 </h1>
          <p class="text-dark/70 mt-1"> 管理您识别和收藏的历史碑文 </p>
        </div>
        <div class="mt-4 md:mt-0 flex space-x-3">
          <button @click="showImportModal"
            class="px-4 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom flex items-center">
            <i class="fas fa-plus mr-2"></i>
            导入碑文
          </button>
          <button @click="showPublishModal"
            class="px-4 py-2 bg-accent text-white rounded-md font-medium hover:bg-accent/90 transition-custom flex items-center">
            <i class="fas fa-upload mr-2"></i>
            发布碑文
          </button>
          <button
            class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md font-medium hover:bg-gray-50 transition-custom flex items-center">
            <i class="fas fa-filter mr-2"></i>
            筛选
          </button>
        </div>
      </div>
      <!-- [/MODULE] e5f_我的碑文页面:页面标题 -- 包含页面标题、新建碑文按钮和筛选按钮 -->

      <!-- [MODULE] f6g_我的碑文页面:内容标签页 -->
      <div class="mb-8 border-b border-gray-200">
        <nav class="flex space-x-8">
          <button @click="activeTab = 'my-recognitions'" :class="[
            'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
            activeTab === 'my-recognitions'
              ? 'border-primary text-primary'
              : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
          ]">
            我的识别
          </button>
          <button @click="activeTab = 'my-collections'" :class="[
            'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
            activeTab === 'my-collections'
              ? 'border-primary text-primary'
              : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
          ]">
            我的收藏
          </button>
          <button @click="activeTab = 'my-downloads'" :class="[
            'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
            activeTab === 'my-downloads'
              ? 'border-primary text-primary'
              : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
          ]">
            我的下载
          </button>
        </nav>
      </div>
      <!-- [/MODULE] f6g_我的碑文页面:内容标签页 -- 包含我的识别、我的收藏和我的下载三个标签页切换 -->

      <!-- [MODULE] f6g_我的碑文页面:发布碑文弹窗 -->
      <div v-if="showPublish" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
          <!-- 弹窗头部 -->
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-medium text-primary"> 发布碑文 </h3>
            <button @click="showPublish = false" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <!-- 弹窗内容 -->
          <div class="px-6 py-4 flex-grow overflow-y-auto">
            <p class="text-dark/70 mb-4"> 请选择要发布至碑文知识库的碑文： </p>
            <!-- 碑文列表 -->
            <div class="space-y-3">
              <!-- 碑文项1 -->
              <div
                class="border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-custom flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mr-3">
                    <i class="fas fa-file-alt text-primary"></i>
                  </div>
                  <div>
                    <h4 class="font-medium"> 汉代张迁碑 </h4>
                    <p class="text-sm text-dark/60"> 识别于 2023-11-15 </p>
                  </div>
                </div>
                <input class="text-primary focus:ring-primary" name="inscription" type="radio" value="1">
              </div>
              <!-- 碑文项2 -->
              <div
                class="border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-custom flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mr-3">
                    <i class="fas fa-file-alt text-primary"></i>
                  </div>
                  <div>
                    <h4 class="font-medium"> 唐代九成宫醴泉铭 </h4>
                    <p class="text-sm text-dark/60"> 识别于 2023-11-10 </p>
                  </div>
                </div>
                <input class="text-primary focus:ring-primary" name="inscription" type="radio" value="2">
              </div>
              <!-- 碑文项3 -->
              <div
                class="border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-custom flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mr-3">
                    <i class="fas fa-file-alt text-primary"></i>
                  </div>
                  <div>
                    <h4 class="font-medium"> 秦代泰山刻石 </h4>
                    <p class="text-sm text-dark/60"> 识别于 2023-11-05 </p>
                  </div>
                </div>
                <input class="text-primary focus:ring-primary" name="inscription" type="radio" value="3">
              </div>
            </div>
          </div>
          <!-- 弹窗底部 -->
          <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
            <button @click="showPublish = false"
              class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md font-medium hover:bg-gray-50 transition-custom">
              取消
            </button>
            <button @click="confirmPublish"
              class="px-4 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom">
              确认发布
            </button>
          </div>
        </div>
      </div>
      <!-- [/MODULE] f6g_我的碑文页面:发布碑文弹窗 -- 用于选择并发布保存的碑文，包含碑文列表选择和确认发布功能 -->

      <!-- [MODULE] g7h_我的碑文页面:导入碑文弹窗 -->
      <div v-if="showImport" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
          <!-- 弹窗头部 -->
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-medium text-primary"> 从历史记录导入碑文 </h3>
            <button @click="showImport = false" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <!-- 弹窗内容 -->
          <div class="px-6 py-4 flex-grow overflow-y-auto">
            <p class="text-dark/70 mb-4"> 请选择要导入的历史碑文： </p>
            <!-- 历史碑文列表 -->
            <div class="space-y-3">
              <!-- 历史碑文项1 -->
              <div
                class="border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-custom flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mr-3">
                    <i class="fas fa-history text-primary"></i>
                  </div>
                  <div>
                    <h4 class="font-medium"> 晋代兰亭集序 </h4>
                    <p class="text-sm text-dark/60"> 识别于 2023-10-28 </p>
                  </div>
                </div>
                <input class="text-primary focus:ring-primary" name="import-inscription" type="radio" value="1">
              </div>
              <!-- 历史碑文项2 -->
              <div
                class="border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-custom flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mr-3">
                    <i class="fas fa-history text-primary"></i>
                  </div>
                  <div>
                    <h4 class="font-medium"> 北魏张猛龙碑 </h4>
                    <p class="text-sm text-dark/60"> 识别于 2023-10-20 </p>
                  </div>
                </div>
                <input class="text-primary focus:ring-primary" name="import-inscription" type="radio" value="2">
              </div>
              <!-- 历史碑文项3 -->
              <div
                class="border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-custom flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-secondary rounded-md flex items-center justify-center mr-3">
                    <i class="fas fa-history text-primary"></i>
                  </div>
                  <div>
                    <h4 class="font-medium"> 隋代龙藏寺碑 </h4>
                    <p class="text-sm text-dark/60"> 识别于 2023-10-15 </p>
                  </div>
                </div>
                <input class="text-primary focus:ring-primary" name="import-inscription" type="radio" value="3">
              </div>
            </div>
          </div>
          <!-- 弹窗底部 -->
          <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
            <button @click="showImport = false"
              class="px-4 py-2 border border-gray-300 text-dark/70 rounded-md font-medium hover:bg-gray-50 transition-custom">
              取消
            </button>
            <button @click="confirmImport"
              class="px-4 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom">
              确认导入
            </button>
          </div>
        </div>
      </div>
      <!-- [/MODULE] g7h_我的碑文页面:导入碑文弹窗 -- 用于从历史记录中选择碑文导入至我的保存，包含历史碑文列表选择和确认导入功能 -->

      <!-- [MODULE] g7h_我的碑文页面:我的识别 -->
      <div v-if="activeTab === 'my-recognitions'" class="tab-content">
        <!-- 搜索框 -->
        <div class="mb-6">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i class="fas fa-search text-dark/40"></i>
            </div>
            <input v-model="searchQuery"
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
              placeholder="搜索我的碑文..." type="text">
          </div>
        </div>
        <!-- 识别记录列表 -->
        <div class="space-y-4">
          <!-- 识别记录项1 -->
          <div
            class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-custom">
            <div class="p-5">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between">
                <div class="flex-grow">
                  <div class="flex items-start">
                    <div class="flex-shrink-0 mr-4">
                      <img alt="碑文缩略图" class="w-20 h-20 object-cover rounded-lg"
                        src="/gemdesign/assets/page/1990611432919531520/78d79bc0414f47fafb793501f9e10ad7.png">
                    </div>
                    <div class="flex-grow">
                      <h3 class="font-semibold text-lg text-primary mb-1"> 唐代墓志铭 </h3>
                      <p class="text-dark/70 text-sm line-clamp-2 mb-2">
                        维大唐开元二十有九年，岁次辛巳，秋八月丁丑朔，十三日己丑。故朝散大夫、守秘书少监、集贤院学士、上柱国、赐紫金鱼袋、赠秘书监、江夏李公，字太白，葬于当涂青山之阳... </p>
                      <div class="flex flex-wrap gap-2 mb-2">
                        <span class="text-xs bg-secondary/30 text-primary px-2 py-1 rounded-full"> 唐代 </span>
                        <span class="text-xs bg-gray-100 text-dark/60 px-2 py-1 rounded-full"> 墓志铭 </span>
                      </div>
                      <div class="flex justify-between items-center">
                        <span class="text-xs text-dark/50"> 2023-06-15 14:30 </span>
                        <div class="flex space-x-2">
                          <button @click="editItem(1)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="编辑">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button @click="toggleFavorite(1)"
                            class="text-dark/50 hover:text-primary transition-custom p-1" title="收藏">
                            <i :class="favorites.includes(1) ? 'fas fa-heart text-red-500' : 'far fa-heart'"></i>
                          </button>
                          <button @click="downloadItem(1)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="下载">
                            <i class="fas fa-download"></i>
                          </button>
                          <button @click="deleteItem(1)" class="text-dark/50 hover:text-red-500 transition-custom p-1"
                            title="删除">
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- 识别记录项2 -->
          <div
            class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-custom">
            <div class="p-5">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between">
                <div class="flex-grow">
                  <div class="flex items-start">
                    <div class="flex-shrink-0 mr-4">
                      <img alt="碑文缩略图" class="w-20 h-20 object-cover rounded-lg"
                        src="/gemdesign/assets/page/1990611432919531520/d1192b167358d7db865b3fd76de247a4.png">
                    </div>
                    <div class="flex-grow">
                      <h3 class="font-semibold text-lg text-primary mb-1"> 张迁碑 </h3>
                      <p class="text-dark/70 text-sm line-clamp-2 mb-2"> 君讳迁，字公方，陈留己吾人也。君之先，出自有周，周宣王中兴，有张仲，以孝友为行，披览《诗 ·
                        雅》，焕知其祖。高帝龙兴，有张良，善用筹策，在帷幕之内，决胜负千里之外，析珪于留... </p>
                      <div class="flex flex-wrap gap-2 mb-2">
                        <span class="text-xs bg-secondary/30 text-primary px-2 py-1 rounded-full"> 汉代 </span>
                        <span class="text-xs bg-gray-100 text-dark/60 px-2 py-1 rounded-full"> 碑刻 </span>
                      </div>
                      <div class="flex justify-between items-center">
                        <span class="text-xs text-dark/50"> 2023-06-10 09:15 </span>
                        <div class="flex space-x-2">
                          <button @click="editItem(2)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="编辑">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button @click="toggleFavorite(2)"
                            class="text-dark/50 hover:text-primary transition-custom p-1" title="收藏">
                            <i
                              :class="favorites.includes(2) ? 'fas fa-heart text-red-500' : 'fas fa-heart text-red-500'"></i>
                          </button>
                          <button @click="downloadItem(2)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="下载">
                            <i class="fas fa-download"></i>
                          </button>
                          <button @click="deleteItem(2)" class="text-dark/50 hover:text-red-500 transition-custom p-1"
                            title="删除">
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- 识别记录项3 -->
          <div
            class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-custom">
            <div class="p-5">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between">
                <div class="flex-grow">
                  <div class="flex items-start">
                    <div class="flex-shrink-0 mr-4">
                      <img alt="碑文缩略图" class="w-20 h-20 object-cover rounded-lg"
                        src="/gemdesign/assets/page/1990611432919531520/3456773e1ad6409bc2d2fe3d51aea7dd.png">
                    </div>
                    <div class="flex-grow">
                      <h3 class="font-semibold text-lg text-primary mb-1"> 醉翁亭记碑 </h3>
                      <p class="text-dark/70 text-sm line-clamp-2 mb-2">
                        环滁皆山也。其西南诸峰，林壑尤美，望之蔚然而深秀者，琅琊也。山行六七里，渐闻水声潺潺，而泻出于两峰之间者，酿泉也。峰回路转，有亭翼然临于泉上者，醉翁亭也... </p>
                      <div class="flex flex-wrap gap-2 mb-2">
                        <span class="text-xs bg-secondary/30 text-primary px-2 py-1 rounded-full"> 宋代 </span>
                        <span class="text-xs bg-gray-100 text-dark/60 px-2 py-1 rounded-full"> 散文 </span>
                      </div>
                      <div class="flex justify-between items-center">
                        <span class="text-xs text-dark/50"> 2023-06-05 09:30 </span>
                        <div class="flex space-x-2">
                          <button @click="editItem(3)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="编辑">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button @click="toggleFavorite(3)"
                            class="text-dark/50 hover:text-primary transition-custom p-1" title="收藏">
                            <i
                              :class="favorites.includes(3) ? 'fas fa-heart text-red-500' : 'fas fa-heart text-red-500'"></i>
                          </button>
                          <button @click="downloadItem(3)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="下载">
                            <i class="fas fa-download"></i>
                          </button>
                          <button @click="deleteItem(3)" class="text-dark/50 hover:text-red-500 transition-custom p-1"
                            title="删除">
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- 识别记录项4 -->
          <div
            class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-custom">
            <div class="p-5">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between">
                <div class="flex-grow">
                  <div class="flex items-start">
                    <div class="flex-shrink-0 mr-4">
                      <img alt="碑文缩略图" class="w-20 h-20 object-cover rounded-lg"
                        src="/gemdesign/assets/page/1990611432919531520/a354316878a704fb627e7ef9d6af239c.png">
                    </div>
                    <div class="flex-grow">
                      <h3 class="font-semibold text-lg text-primary mb-1"> 永乐大典序碑 </h3>
                      <p class="text-dark/70 text-sm line-clamp-2 mb-2">
                        昔者宋太宗皇帝命李昉等编辑群书，名曰《太平总类》，凡一千卷。后太宗日览三卷，因改曰《太平御览》。夫其书包罗万象，靡所不有，可谓备矣。然犹有遗憾焉... </p>
                      <div class="flex flex-wrap gap-2 mb-2">
                        <span class="text-xs bg-secondary/30 text-primary px-2 py-1 rounded-full"> 明代 </span>
                        <span class="text-xs bg-gray-100 text-dark/60 px-2 py-1 rounded-full"> 典籍 </span>
                      </div>
                      <div class="flex justify-between items-center">
                        <span class="text-xs text-dark/50"> 2023-05-28 16:45 </span>
                        <div class="flex space-x-2">
                          <button @click="editItem(4)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="编辑">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button @click="toggleFavorite(4)"
                            class="text-dark/50 hover:text-primary transition-custom p-1" title="收藏">
                            <i :class="favorites.includes(4) ? 'fas fa-heart text-red-500' : 'far fa-heart'"></i>
                          </button>
                          <button @click="downloadItem(4)" class="text-dark/50 hover:text-primary transition-custom p-1"
                            title="下载">
                            <i class="fas fa-download"></i>
                          </button>
                          <button @click="deleteItem(4)" class="text-dark/50 hover:text-red-500 transition-custom p-1"
                            title="删除">
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 分页 -->
        <div class="mt-8 flex justify-center">
          <nav class="flex items-center space-x-1">
            <button
              class="px-3 py-2 rounded-md border border-gray-300 text-dark/50 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled>
              <i class="fas fa-chevron-left text-xs"></i>
            </button>
            <button class="px-4 py-2 rounded-md bg-primary text-white border border-primary"> 1 </button>
            <button class="px-4 py-2 rounded-md border border-gray-300 text-dark/70 hover:bg-gray-50"> 2 </button>
            <button class="px-4 py-2 rounded-md border border-gray-300 text-dark/70 hover:bg-gray-50"> 3 </button>
            <span class="px-2 text-dark/50"> ... </span>
            <button class="px-4 py-2 rounded-md border border-gray-300 text-dark/70 hover:bg-gray-50"> 8 </button>
            <button class="px-3 py-2 rounded-md border border-gray-300 text-dark/70 hover:bg-gray-50">
              <i class="fas fa-chevron-right text-xs"></i>
            </button>
          </nav>
        </div>
      </div>
      <!-- [/MODULE] g7h_我的碑文页面:我的识别 -- 展示用户识别过的碑文列表，包含碑文缩略图、标题、内容预览、朝代标签、时间戳和操作按钮 -->

      <!-- [MODULE] h8i_我的碑文页面:我的收藏 -->
      <div v-if="activeTab === 'my-collections'" class="tab-content">
        <div class="bg-white rounded-xl p-8 text-center border border-gray-200">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
            <i class="fas fa-heart text-2xl text-gray-400"></i>
          </div>
          <h3 class="text-lg font-medium text-dark mb-2"> 您还没有收藏任何碑文 </h3>
          <p class="text-dark/60 mb-6 max-w-md mx-auto"> 浏览碑文识别结果或碑文知识库，点击收藏按钮将感兴趣的碑文添加到这里 </p>
          <router-link to="/knowledge">
            <button
              class="px-5 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom">
              去查阅更多碑文
            </button>
          </router-link>
        </div>
      </div>
      <!-- [/MODULE] h8i_我的碑文页面:我的收藏 -- 显示用户收藏的碑文，当前为空状态，提示用户去识别或浏览碑文 -->

      <!-- [MODULE] i9j_我的碑文页面:我的下载 -->
      <div v-if="activeTab === 'my-downloads'" class="tab-content">
        <div class="bg-white rounded-xl p-8 text-center border border-gray-200">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
            <i class="fas fa-download text-2xl text-gray-400"></i>
          </div>
          <h3 class="text-lg font-medium text-dark mb-2"> 您还没有下载任何碑文 </h3>
          <p class="text-dark/60 mb-6 max-w-md mx-auto"> 点击下载按钮将碑文内容保存到本地，在此处可以离线查看碑文 </p>
          <router-link to="/knowledge">
            <button
              class="px-5 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom">
              去保存碑文
            </button>
          </router-link>
        </div>
      </div>
      <!-- [/MODULE] i9j_我的碑文页面:我的下载 -- 显示用户下载的碑文，当前为空状态，提示用户去识别碑文 -->
    </div>
  </section>
  <!-- [/MODULE] d4e_我的碑文页面 -- 展示用户的碑文管理中心，包含我的识别、我的收藏和我的下载三个标签页内容 -->
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/app'

const appStore = useAppStore()

// 响应式数据
const activeTab = ref('my-recognitions')
const searchQuery = ref('')
const showPublish = ref(false)
const showImport = ref(false)
const favorites = ref([2, 3]) // 示例数据：已收藏的项目ID

// 显示发布弹窗
const showPublishModal = () => {
  showPublish.value = true
}

// 显示导入弹窗
const showImportModal = () => {
  showImport.value = true
}

// 确认发布
const confirmPublish = () => {
  const selected = document.querySelector('input[name="inscription"]:checked')
  if (selected) {
    alert(`确认发布: ${selected.value}`)
    showPublish.value = false
  } else {
    alert('请选择要发布的碑文')
  }
}

// 确认导入
const confirmImport = () => {
  const selected = document.querySelector('input[name="import-inscription"]:checked')
  if (selected) {
    alert(`确认导入: ${selected.value}`)
    showImport.value = false
  } else {
    alert('请选择要导入的碑文')
  }
}

// 编辑项目
const editItem = (id) => {
  alert(`编辑碑文: ${id}`)
}

// 切换收藏状态
const toggleFavorite = (id) => {
  const index = favorites.value.indexOf(id)
  if (index > -1) {
    favorites.value.splice(index, 1)
  } else {
    favorites.value.push(id)
  }
}

// 下载项目
const downloadItem = (id) => {
  alert(`下载碑文: ${id}`)
}

// 删除项目
const deleteItem = (id) => {
  if (confirm('确定要删除这条碑文记录吗？')) {
    alert(`删除碑文: ${id}`)
  }
}
</script>
