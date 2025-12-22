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
          <button @click="showImportModal = true" class="px-4 py-2 bg-white border border-gray-300 text-dark rounded-md font-medium hover:bg-gray-50 transition-custom flex items-center">
            <i class="fas fa-file-import mr-2 text-primary"></i>
            导入碑文
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
          <button @click="activeTab = 'my-imports'; loadImportsHistory()" :class="[
            'py-4 px-1 border-b-2 font-medium text-sm md:text-base whitespace-nowrap',
            activeTab === 'my-imports'
              ? 'border-primary text-primary'
              : 'border-transparent text-dark/50 hover:text-dark/70 hover:border-gray-300'
          ]">
            我的导入
          </button>
        </nav>
      </div>
      <!-- [/MODULE] f6g_我的碑文页面:内容标签页 -- 包含我的识别、我的收藏和我的下载三个标签页切换 -->

      <!-- 编辑碑文弹窗 -->
      <div v-if="showEditModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg w-full max-w-lg flex flex-col animate-fade-in-up">
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-medium text-primary">编辑碑文</h3>
            <button @click="showEditModal = false" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-dark mb-2">标题</label>
              <input v-model="editForm.title" class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:border-primary" placeholder="请输入标题">
            </div>
            <div>
              <label class="block text-sm font-medium text-dark mb-2">内容</label>
              <textarea v-model="editForm.content" rows="6" class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:border-primary" placeholder="请输入内容"></textarea>
            </div>
          </div>
          <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
            <button @click="showEditModal = false" class="px-4 py-2 text-dark/70 hover:text-dark">取消</button>
            <button @click="submitEdit" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 disabled:opacity-50" :disabled="editing">
              {{ editing ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>

      <!-- [MODULE] g7h_我的碑文页面:导入碑文弹窗 -->
      <div v-if="showImportModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg w-full max-w-lg flex flex-col animate-fade-in-up">
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-medium text-primary">导入碑文</h3>
            <button @click="showImportModal = false" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="p-6">
            <div 
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer bg-gray-50"
              @click="$refs.fileInput.click()"
              @dragover.prevent
              @drop.prevent="handleDrop"
            >
              <input type="file" ref="fileInput" multiple accept=".json" class="hidden" @change="handleFileSelect">
              <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-3"></i>
              <p class="text-dark font-medium mb-1">点击或拖拽文件到此处</p>
              <p class="text-xs text-dark/50">仅支持 JSON 格式</p>
            </div>

            <div v-if="selectedFiles.length > 0" class="mt-4 max-h-40 overflow-y-auto space-y-2">
              <div v-for="(file, index) in selectedFiles" :key="index" class="flex justify-between items-center bg-gray-50 p-2 rounded text-sm">
                <span class="truncate max-w-[200px]">{{ file.name }}</span>
                <span class="text-xs text-gray-400">{{ (file.size / 1024).toFixed(1) }} KB</span>
                <button @click.stop="removeFile(index)" class="text-red-400 hover:text-red-600 ml-2">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>

            <div class="mt-4 flex justify-between items-center" v-if="importing">
               <span class="text-sm text-primary">正在导入...</span>
               <div class="w-1/2 bg-gray-200 rounded-full h-2">
                  <div class="bg-primary h-2 rounded-full animate-pulse w-full"></div>
               </div>
            </div>
          </div>
          
          <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
            <button @click="showImportModal = false" class="px-4 py-2 text-dark/70 hover:text-dark">取消</button>
            <button 
              @click="submitImport" 
              class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 disabled:opacity-50"
              :disabled="selectedFiles.length === 0 || importing"
            >
              {{ importing ? '导入中...' : '开始导入' }}
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
        <div v-if="loading" class="space-y-4">
          <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 p-6 text-center">
            <i class="fas fa-spinner fa-spin text-primary"></i>
          </div>
        </div>
        <div v-else-if="filteredItems.length > 0" class="space-y-4">
          <!-- 调试信息：输出filteredItems数组内容 -->
          <div v-if="false" class="bg-yellow-50 p-4 rounded-lg text-sm">
            <h4 class="font-medium mb-2">调试信息 - filteredItems:</h4>
            <pre class="whitespace-pre-wrap text-xs overflow-auto max-h-40 bg-white p-2 rounded">{{ JSON.stringify(filteredItems, null, 2) }}</pre>
          </div>
          
          <div v-for="it in filteredItems" :key="it.id" 
            class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-custom cursor-pointer"
            @click="router.push(`/my-inscriptions/${it.id}`)"
          >
            <!-- 调试信息：输出当前项的图片相关字段 -->
            <div v-if="false" class="bg-blue-50 p-2 rounded text-xs">
              ID: {{ it.id }}<br>
              cover_image_url: {{ it.cover_image_url }}<br>
              image_url: {{ it.image_url }}<br>
              cover_image: {{ it.cover_image }}<br>
              最终图片URL: {{ it.cover_image_url || it.image_url || it.cover_image || 'https://via.placeholder.com/80x80?text=No+Image' }}
            </div>
            <div class="p-5">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between">
                <div class="flex-grow">
                  <div class="flex items-start">
                    <div class="flex-shrink-0 mr-4">
                      <img :alt="it.title" class="w-20 h-20 object-cover rounded-lg" :src="it.cover_image_url || it.image_url || it.cover_image || 'https://via.placeholder.com/80x80?text=No+Image'">
                    </div>
                    <div class="flex-grow">
                      <h3 class="font-semibold text-lg text-primary mb-1">{{ it.title }}</h3>
                      <p class="text-dark/70 text-sm line-clamp-2 mb-2">{{ it.text || it.content }}</p>
                      <div class="flex flex-wrap gap-2 mb-2">
                        <span v-if="it.dynasty" class="text-xs bg-secondary/30 text-primary px-2 py-1 rounded-full">{{ it.dynasty }}</span>
                        <span v-if="it.category" class="text-xs bg-gray-100 text-dark/60 px-2 py-1 rounded-full">{{ it.category }}</span>
                      </div>
                      <div class="flex justify-between items-center">
                        <span class="text-xs text-dark/50">{{ it.created_at || '' }}</span>
                        <div class="flex space-x-2" @click.stop>
                          <button @click="downloadItem(it.id)" class="text-dark/50 hover:text-primary transition-custom p-1" title="下载">
                            <i class="fas fa-download"></i>
                          </button>
                          <button @click="deleteItem(it.id)" class="text-dark/50 hover:text-red-500 transition-custom p-1" title="删除">
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
        <div v-else-if="false" class="space-y-4">
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
        <div v-if="filteredItems.length > 0" class="mt-8 flex justify-center">
          <nav class="flex items-center space-x-1">
            <button @click="prevPage" class="px-3 py-2 rounded-md border border-gray-300 text-dark/50 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="page === 1">
              <i class="fas fa-chevron-left text-xs"></i>
            </button>
            <button class="px-4 py-2 rounded-md bg-primary text-white border border-primary">{{ page }}</button>
            <button @click="nextPage" class="px-3 py-2 rounded-md border border-gray-300 text-dark/70 hover:bg-gray-50">
              <i class="fas fa-chevron-right text-xs"></i>
            </button>
          </nav>
        </div>
        <!-- 分页 -->
        <div v-if="false" class="mt-8 flex justify-center">
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
        <div v-if="favoritesLoading" class="bg-white rounded-xl p-8 text-center border border-gray-200">
          <i class="fas fa-spinner fa-spin text-primary"></i>
        </div>
        <div v-else-if="favoritesItems.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="fav in favoritesItems" :key="fav.id" 
            class="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-custom border border-gray-100 cursor-pointer"
            @click="router.push(`/knowledge/article/${fav.id}`)"
          >
            <div class="h-36 overflow-hidden bg-gray-100">
              <img :src="fav.cover_image || 'https://via.placeholder.com/400x200?text=No+Image'" :alt="fav.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105">
            </div>
            <div class="p-4">
              <div class="flex justify-between items-center mb-2">
                <span v-if="fav.dynasty" class="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">{{ fav.dynasty }}</span>
                <span v-if="fav.category" class="text-xs bg-secondary/30 text-primary px-2 py-0.5 rounded">{{ fav.category }}</span>
              </div>
              <h3 class="text-lg font-semibold mb-2 line-clamp-2 text-primary hover:text-primary/80 transition-custom">
                {{ fav.title }}
              </h3>
              <p class="text-sm text-dark/70 line-clamp-2 mb-3">
                {{ fav.content }}
              </p>
              <div class="flex justify-between items-center text-xs text-dark/50">
                <span>{{ fav.created_at ? new Date(fav.created_at).toLocaleDateString() : '' }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="bg-white rounded-xl p-8 text-center border border-gray-200">
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
        <div v-if="downloadHistory.length > 0" class="space-y-4">
          <div v-for="item in downloadHistory" :key="item.id" 
            class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 p-5 flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center mr-4">
                <i :class="getFileIcon(item.format)" class="text-xl text-primary"></i>
              </div>
              <div>
                <h3 class="font-semibold text-dark">{{ item.title }}</h3>
                <p class="text-xs text-dark/50">{{ item.date }} · {{ item.size }} · {{ item.format.toUpperCase() }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <span v-if="item.status === 'completed'" class="text-xs text-green-500 bg-green-50 px-2 py-1 rounded">已完成</span>
              <span v-else class="text-xs text-blue-500 bg-blue-50 px-2 py-1 rounded">下载中 {{ item.progress }}%</span>
              <button @click="downloadFile(item)" class="text-dark/50 hover:text-primary transition-custom p-2">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="bg-white rounded-xl p-8 text-center border border-gray-200">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
            <i class="fas fa-download text-2xl text-gray-400"></i>
          </div>
          <h3 class="text-lg font-medium text-dark mb-2"> 您还没有下载任何碑文 </h3>
          <p class="text-dark/60 mb-6 max-w-md mx-auto"> 点击下载按钮将碑文内容保存到本地，在此处可以离线查看碑文 </p>
          <button @click="activeTab = 'my-recognitions'"
            class="px-5 py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-custom">
            去下载碑文
          </button>
        </div>
      </div>
      <!-- [/MODULE] i9j_我的碑文页面:我的下载 -->

      <!-- 我的导入 -->
      <div v-if="activeTab === 'my-imports'" class="tab-content">
        <div class="grid lg:grid-cols-3 gap-6">
          <div class="lg:col-span-1">
            <div class="bg-white rounded-xl shadow-sm p-4">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-lg font-semibold">导入列表</h3>
                <button @click="loadImportsHistory" class="text-sm text-primary">刷新</button>
              </div>
              <div v-if="importsLoading" class="text-center p-4">
                <i class="fas fa-spinner fa-spin text-primary"></i>
              </div>
              <div v-else-if="importHistory.length > 0" class="space-y-2 max-h-80 overflow-y-auto">
                <div v-for="it in importHistory" :key="it.id" class="p-2 border rounded cursor-pointer hover:bg-gray-50" @click="router.push(`/my-imports/${it.id}`)">
                  <div class="text-sm font-medium">{{ it.title || it.filename }}</div>
                  <div class="text-xs text-dark/50">{{ it.filename }} · {{ it.created_at }}</div>
                </div>
              </div>
              <div v-else class="text-sm text-dark/60">暂无导入记录，请先在“导入碑文”上传</div>
            </div>
          </div>

        </div>
      </div>

      <!-- 下载格式选择弹窗 -->
      <div v-if="showDownloadModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg w-full max-w-sm flex flex-col animate-fade-in-up">
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-medium text-primary">选择下载格式</h3>
            <button @click="showDownloadModal = false" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="p-4 space-y-2">
            <button @click="startDownload('json')" class="w-full flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-custom">
              <span class="flex items-center"><i class="fas fa-code text-yellow-500 mr-3"></i> JSON 数据</span>
              <span class="text-xs text-gray-400">完整数据结构</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 下载进度弹窗 -->
      <div v-if="downloadProgress > 0 && downloadProgress < 100" class="fixed bottom-4 right-4 z-50 bg-white rounded-lg shadow-lg p-4 w-80 border border-gray-200 animate-slide-in-right">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm font-medium text-dark">正在下载...</span>
          <span class="text-xs text-primary">{{ downloadProgress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-primary h-2 rounded-full transition-all duration-300" :style="{ width: downloadProgress + '%' }"></div>
        </div>
      </div>
    </div>
  </section>
  <!-- [/MODULE] d4e_我的碑文页面 -- 展示用户的碑文管理中心，包含我的识别、我的收藏和我的下载三个标签页内容 -->
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { listMyInscriptions, deleteInscription } from '../api/inscription'
import { fetchArticleDetail } from '../api/knowledge'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const activeTab = ref('my-recognitions')
const searchQuery = ref('')
const favorites = ref([])
const items = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const favoritesItems = ref([])
const favoritesLoading = ref(false)

// 下载相关
const downloadHistory = ref([])
const showDownloadModal = ref(false)
const currentDownloadId = ref(null)
const downloadProgress = ref(0)

// 导入相关
const showImportModal = ref(false) // Replaces showImport
const selectedFiles = ref([])
const importing = ref(false)
// 我的导入子页
const importsLoading = ref(false)
const importHistory = ref([])
const selectedImport = ref(null)
const importEditTitle = ref('')
const importEditContent = ref('')
const importCategory = ref('')
const importTags = ref([])
const importNewTag = ref('')

const filteredItems = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return items.value
  return (items.value || []).filter(it => {
    const title = (it.title || '').toLowerCase()
    const content = (it.content || '').toLowerCase()
    return title.includes(q) || content.includes(q)
  })
})

const showEditModal = ref(false)
const editForm = ref({
  id: '',
  title: '',
  content: ''
})
const editing = ref(false)

const editItem = (id) => {
  const item = items.value.find(it => it.id === id)
  if (!item) return
  
  editForm.value = {
    id: item.id,
    title: item.title,
    content: item.content
  }
  showEditModal.value = true
}

const submitEdit = async () => {
  if (!editForm.value.title || !editForm.value.content) {
    appStore.addNotification({ type: 'error', message: '标题和内容不能为空', duration: 2000 })
    return
  }
  
  editing.value = true
  try {
    const baseUrl = window.location.origin + '/api/v1'
    const token = localStorage.getItem('token') || ''
    
    const response = await fetch(`${baseUrl}/inscription/${editForm.value.id}`, {
      method: 'PUT',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: editForm.value.title,
        content: editForm.value.content,
        // updatedAt: new Date().toISOString() // 后端通常自动处理
      })
    })
    
    if (response.ok) {
      appStore.addNotification({ type: 'success', message: '保存成功', duration: 2000 })
      showEditModal.value = false
      loadList() // 刷新列表
    } else {
      throw new Error('Update failed')
    }
  } catch (e) {
    appStore.addNotification({ type: 'error', message: '保存失败，请重试', duration: 2000 })
  } finally {
    editing.value = false
  }
}

const toggleFavorite = async (id) => {
  const isFavorited = favorites.value.includes(id)
  const baseUrl = window.location.origin + '/api/v1'
  const token = localStorage.getItem('token') || ''
  
  try {
    // 乐观更新
    if (isFavorited) {
      favorites.value = favorites.value.filter(fid => fid !== id)
    } else {
      favorites.value = [...favorites.value, id]
    }

    if (isFavorited) {
       await fetch(`${baseUrl}/favorite/${id}`, {
         method: 'DELETE',
         headers: { 'Authorization': `Bearer ${token}` }
       })
       appStore.addNotification({ type: 'success', message: '已取消收藏', duration: 1000 })
    } else {
       await fetch(`${baseUrl}/favorite/add`, {
         method: 'POST',
         headers: { 
           'Authorization': `Bearer ${token}`,
           'Content-Type': 'application/json'
         },
         body: JSON.stringify({ itemId: id })
       })
       appStore.addNotification({ type: 'success', message: '收藏成功', duration: 1000 })
    }

    if (activeTab.value === 'my-collections') {
      loadCollections()
    }
  } catch (e) {
    // 回滚
    if (isFavorited) {
       favorites.value = [...favorites.value, id]
    } else {
       favorites.value = favorites.value.filter(fid => fid !== id)
    }
    appStore.addNotification({ type: 'error', message: '操作失败，请重试', duration: 2000 })
  }
}

const getFileIcon = (format) => {
  const map = {
    'pdf': 'fas fa-file-pdf',
    'txt': 'fas fa-file-alt',
    'image': 'fas fa-image'
  }
  return map[format] || 'fas fa-file'
}

const downloadItem = (id) => {
  currentDownloadId.value = id
  showDownloadModal.value = true
}

const startDownload = async (format) => {
  showDownloadModal.value = false
  if (!currentDownloadId.value) return
  
  const item = items.value.find(it => it.id === currentDownloadId.value) || 
               favoritesItems.value.find(it => it.id === currentDownloadId.value)
  
  if (!item) return

  // 模拟下载过程
  downloadProgress.value = 0
  const historyItem = {
    id: Date.now(),
    title: item.title,
    format: format,
    size: '计算中...',
    date: new Date().toLocaleDateString(),
    status: 'downloading',
    progress: 0,
    url: '' // 真实环境应从后端获取
  }
  
  downloadHistory.value.unshift(historyItem)
  // 保存到本地
  localStorage.setItem('downloadHistory', JSON.stringify(downloadHistory.value))
  
  // 模拟进度
  const timer = setInterval(() => {
    downloadProgress.value += 10
    historyItem.progress = downloadProgress.value
    
    if (downloadProgress.value >= 100) {
      clearInterval(timer)
      historyItem.status = 'completed'
      historyItem.size = (Math.random() * 5 + 1).toFixed(1) + ' MB'
      localStorage.setItem('downloadHistory', JSON.stringify(downloadHistory.value))
      downloadProgress.value = 0
      appStore.addNotification({ type: 'success', message: `${item.title} 下载完成`, duration: 3000 })
      
      // 触发真实文件下载（调用后端API）
      triggerFileDownload(currentDownloadId.value, format, item.title)
    }
  }, 300)
}

const triggerFileDownload = async (id, format, filename) => {
  const baseUrl = window.location.origin + '/api/v1'
  const token = localStorage.getItem('token') || ''
  try {
    const response = await fetch(`${baseUrl}/inscription/${id}/download?format=${format}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.${format === 'image' ? 'jpg' : format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } else {
      console.warn('后端下载接口未就绪，仅演示进度')
    }
  } catch (e) {
    console.error('下载请求失败', e)
  }
}

const downloadFile = (item) => {
  // 重新下载历史记录中的文件
  appStore.addNotification({ type: 'info', message: '开始重新下载...', duration: 2000 })
  triggerFileDownload(currentDownloadId.value || 1, item.format, item.title) // 简化处理，实际应存ID
}

const deleteItem = async (id) => {
  if (!confirm('确定要删除这条碑文记录吗？')) return
  try {
    const baseUrl = window.location.origin
    const token = localStorage.getItem('token') || ''
    await deleteInscription({ baseUrl, token, id })
    items.value = (items.value || []).filter(it => String(it.id) !== String(id))
    total.value = Math.max(0, total.value - 1)
    appStore.addNotification({ type: 'success', message: '删除成功', duration: 2000 })
  } catch (e) {
    appStore.addNotification({ type: 'error', message: '删除失败，请稍后重试', duration: 3000 })
  }
}

const loadList = async () => {
  try {
    loading.value = true
    const baseUrl = window.location.origin
    const token = localStorage.getItem('token') || ''
    console.log('加载我的碑文列表, page:', page.value)
    const data = await listMyInscriptions({ baseUrl, token, page: page.value, size: size.value, q: searchQuery.value })
    const list = Array.isArray(data.list) ? data.list : (Array.isArray(data.records) ? data.records : [])
    // 调试：输出原始数据结构
    console.log('API返回的原始数据:', list)
    
    const remoteItems = (list || []).map(it => {
      // 调试：输出每个项的原始数据
      console.log('原始项数据:', it)
      
      return {
        id: it.id,
        title: it.title || '我的碑文',
        content: it.content || it.text || '',
        dynasty: it.dynasty || '',
        category: it.category || '',
        created_at: it.created_at || it.date || '',
        image_url: it.image_url || '',
        cover_image: it.cover_image || '',
        // 添加cover_image_url字段的映射
        cover_image_url: it.cover_image_url || '',
        confidence: it.confidence || 0
      }
    })
    
    // 调试：输出处理后的items
    console.log('处理后的items:', remoteItems)
    items.value = remoteItems
    total.value = parseInt(data.total || 0, 10) || 0
  } catch (e) {
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const prevPage = async () => {
  if (page.value <= 1) return
  page.value -= 1
  await loadList()
}

const nextPage = async () => {
  const maxPage = Math.max(1, Math.ceil(total.value / size.value))
  if (page.value >= maxPage) return
  page.value += 1
  await loadList()
}

onMounted(() => {
  const stored = localStorage.getItem('favorites')
  if (stored) {
    try {
      favorites.value = JSON.parse(stored)
    } catch (e) {
      favorites.value = []
    }
  }
  
  if (route.query.tab === 'my-collections') {
    activeTab.value = 'my-collections'
  }
  
  // 加载下载历史
  const history = localStorage.getItem('downloadHistory')
  if (history) {
    try {
      downloadHistory.value = JSON.parse(history)
    } catch (e) {
      downloadHistory.value = []
    }
  }
  
  loadList()
  loadCollections()
  // 预加载导入历史
  loadImportsHistory()
})

// 导入相关逻辑
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addFiles(files)
  event.target.value = '' // reset
}

const handleDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  addFiles(files)
}

const addFiles = (files) => {
  const validFiles = files.filter(f => (f.name || '').toLowerCase().endsWith('.json'))
  selectedFiles.value = [...selectedFiles.value, ...validFiles]
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const submitImport = async () => {
  if (selectedFiles.value.length === 0) return
  
  importing.value = true
  const formData = new FormData()
  selectedFiles.value.forEach(file => {
    formData.append('files', file)
  })
  
  try {
    const baseUrl = window.location.origin + '/api/v1'
    const token = localStorage.getItem('token') || ''
    const response = await fetch(`${baseUrl}/imports/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })
    
    if (response.ok) {
      const result = await response.json()
      const data = result.data || {}
      
      // 显示详细失败信息
      const failedItems = (data.items || []).filter(it => it.status === 'failed')
      if (failedItems.length > 0) {
        let msg = `成功 ${data.count || 0} 个，失败 ${data.failed || 0} 个`
        if (failedItems.length <= 3) {
           msg += '：' + failedItems.map(it => `${it.filename} (${it.reason})`).join('; ')
        } else {
           msg += '，请检查文件格式'
        }
        appStore.addNotification({ type: 'warning', message: msg, duration: 5000 })
      } else {
        appStore.addNotification({ type: 'success', message: `成功导入 ${data.count || 0} 个文件`, duration: 3000 })
      }

      showImportModal.value = false
      selectedFiles.value = []
      activeTab.value = 'my-imports'
      await loadImportsHistory()
    } else {
      throw new Error('Import failed')
    }
  } catch (e) {
    appStore.addNotification({ type: 'error', message: '导入失败，请检查文件格式', duration: 3000 })
  } finally {
    importing.value = false
  }
}

// 我的导入子页逻辑
const loadImportsHistory = async () => {
  const baseUrl = window.location.origin + '/api/v1'
  const token = localStorage.getItem('token') || ''
  try {
    importsLoading.value = true
    const res = await fetch(`${baseUrl}/imports/list`, { headers: { 'Authorization': `Bearer ${token}` } })
    if (res.ok) {
      const json = await res.json()
      importHistory.value = json.data || []
    } else {
      importHistory.value = []
    }
  } catch {
    importHistory.value = []
  } finally {
    importsLoading.value = false
  }
}

const selectImport = (item) => {
  selectedImport.value = item
  importEditTitle.value = item.title || item.filename || ''
  importEditContent.value = item.content || item.preview || ''
  importCategory.value = ''
  importTags.value = []
  importNewTag.value = ''
}

const addImportTag = () => {
  const t = importNewTag.value.trim()
  if (!t) return
  importTags.value = [...importTags.value, t]
  importNewTag.value = ''
}
const removeImportTag = (idx) => {
  importTags.value.splice(idx, 1)
}
const toUpperImport = () => { importEditContent.value = (importEditContent.value || '').toUpperCase() }
const toLowerImport = () => { importEditContent.value = (importEditContent.value || '').toLowerCase() }
const trimSpacesImport = () => { importEditContent.value = (importEditContent.value || '').replace(/\s+/g, ' ').trim() }


const loadCollections = async () => {
  try {
    favoritesLoading.value = true
    const baseUrl = window.location.origin + '/api/v1'
    const token = localStorage.getItem('token') || ''
    
    // 获取收藏列表
    const res = await fetch(`${baseUrl}/favorite/list`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    let ids = []
    if (res.ok) {
        const json = await res.json()
        ids = json.data || []
        favorites.value = ids // 同步状态
    } else {
        // 降级到本地
        ids = JSON.parse(localStorage.getItem('favorites') || '[]')
    }

    if (!Array.isArray(ids) || ids.length === 0) {
      favoritesItems.value = []
      return
    }
    
    const results = []
    for (const id of ids) {
      try {
        const article = await fetchArticleDetail(baseUrl, token, id)
        results.push({
          id: article.id,
          title: article.title || '收藏碑文',
          content: article.excerpt || article.description || '',
          dynasty: article.dynasty || '',
          category: article.metadata?.category || '',
          created_at: article.created_at || '',
          image_url: article.cover_image || '',
          cover_image: article.cover_image || '',
          confidence: 0
        })
      } catch {}
    }
    favoritesItems.value = results
  } finally {
    favoritesLoading.value = false
  }
}
</script>
