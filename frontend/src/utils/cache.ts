import type { AxiosRequestConfig, AxiosResponse, AxiosRequestHeaders } from 'axios';
import axios from 'axios';

// 扩展AxiosRequestConfig以支持cache属性
interface CachedAxiosRequestConfig extends AxiosRequestConfig {
  cache?: boolean | number;
}

// 缓存接口
interface CacheEntry {
 data: unknown;
 timestamp: number;
 ttl: number;
}
interface CacheConfig {
 enabled: boolean;
 ttl: number; // 缓存时间（秒）
 maxSize: number; // 最大缓存条目数
}
// 默认缓存配置
const DEFAULT_CACHE_CONFIG: CacheConfig = {
 enabled: true,
 ttl: 300,
 maxSize: 100
};
// 缓存存储
const cache = new Map<string, CacheEntry>();
// 缓存配置
let cacheConfig = { ...DEFAULT_CACHE_CONFIG };
// 设置缓存配置
export const setCacheConfig = (config: Partial<CacheConfig>) => {
 cacheConfig = { ...cacheConfig, ...config };
};
// 生成缓存键
const generateCacheKey = (config: AxiosRequestConfig): string => {
 const { method = 'get', url = '', params = {}, data = {} } = config;
 const paramsStr = params ? JSON.stringify(params) : '';
 const dataStr = data ? JSON.stringify(data) : '';
 return `${method}:${url}:${paramsStr}:${dataStr}`;
};
// 获取缓存
const getCache = (key: string): CacheEntry | null => {
 if (!cacheConfig.enabled)
 return null;
 const entry = cache.get(key);
 if (!entry)
 return null;
 // 检查是否过期
 if (Date.now() - entry.timestamp > entry.ttl * 1000) {
 cache.delete(key);
 return null;
 }
 return entry;
};
// 设置缓存
const setCache = (key: string, data: unknown, ttl?: number) => {
 if (!cacheConfig.enabled)
 return;
 // 如果缓存已满，移除最旧的条目
 if (cache.size >= cacheConfig.maxSize) {
 const oldestKey = Array.from(cache.keys()).reduce((oldest, key) => {
 const entry = cache.get(key);
 const oldestEntry = cache.get(oldest);
 return entry && oldestEntry && entry.timestamp < oldestEntry.timestamp ? key : oldest;
 });
 cache.delete(oldestKey);
 }
 cache.set(key, {
 data,
 timestamp: Date.now(),
 ttl: ttl || cacheConfig.ttl
 });
};
// 清除缓存
export const clearCache = (key?: string) => {
 if (key) {
 cache.delete(key);
 }
 else {
 cache.clear();
 }
};
// 获取缓存大小
export const getCacheSize = (): number => {
 return cache.size;
};
// 缓存请求拦截器
export const createCachedAxios = (instance: typeof axios) => {
 const originalRequest = instance.request.bind(instance);
 // @ts-ignore - 自定义缓存逻辑与原始类型不完全匹配
 instance.request = async function <T = unknown>(config: CachedAxiosRequestConfig): Promise<AxiosResponse<T>> {
 // 只缓存GET请求
 if (config.method?.toLowerCase() !== 'get' || !config.cache) {
 return originalRequest(config) as Promise<AxiosResponse<T>>;
 }
 const cacheKey = generateCacheKey(config);
 const cachedEntry = getCache(cacheKey);
 if (cachedEntry) {
 console.debug(`[Cache] Hit: ${config.url}`);
 return Promise.resolve({
 data: cachedEntry.data as T,
 status: 200,
 statusText: 'OK',
 headers: {} as AxiosRequestHeaders,
 config: config as AxiosRequestConfig
 }) as Promise<AxiosResponse<T>>;
 }
 const response = await originalRequest(config);
 // 设置缓存（使用配置的ttl或默认值）
 const ttl = typeof config.cache === 'number' ? config.cache : undefined;
 setCache(cacheKey, response.data, ttl);
 console.debug(`[Cache] Set: ${config.url}`);
 return response as AxiosResponse<T>;
 };
 return instance;
};
// 带缓存的请求方法
export const cachedGet = async <T = unknown>(url: string, config?: AxiosRequestConfig & {
 cache?: boolean | number;
}): Promise<AxiosResponse<T>> => {
 const requestConfig: AxiosRequestConfig & {
 cache?: boolean | number;
 } = {
 ...config,
 method: 'get',
 url,
 cache: config?.cache !== undefined ? config.cache : true
 };
 return axios.request<T>(requestConfig);
};
// 清除特定URL的缓存
export const clearCacheByUrl = (url: string) => {
 cache.forEach((_, key) => {
 if (key.startsWith(`get:${url}`)) {
 cache.delete(key);
 }
 });
};
export { cache };
