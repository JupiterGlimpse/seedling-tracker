#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

// 使用stealth插件避免被反爬虫检测
puppeteer.use(StealthPlugin());

const server = new Server(
  {
    name: 'boss-scraper',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 列出可用的工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'search_jobs',
      description: '在Boss直聘上搜索职位信息。支持关键词和城市筛选，返回职位列表包含公司、职位、薪资、JD等信息。',
      inputSchema: {
        type: 'object',
        properties: {
          keyword: {
            type: 'string',
            description: '搜索关键词，如"AI产品经理"、"Python开发"等',
          },
          city: {
            type: 'string',
            description: '城市代码，如"101010100"（北京）、"101020100"（上海）、"101280100"（广州）、"101280600"（深圳）',
          },
          experience: {
            type: 'string',
            description: '工作经验要求，可选值：101（应届生）、102（1年以内）、103（1-3年）、104（3-5年）、105（5-10年）、106（10年以上）',
          },
          page: {
            type: 'number',
            description: '页码，默认为1',
            default: 1,
          },
        },
        required: ['keyword', 'city'],
      },
    },
    {
      name: 'get_job_detail',
      description: '获取Boss直聘上单个职位的详细信息',
      inputSchema: {
        type: 'object',
        properties: {
          url: {
            type: 'string',
            description: '职位详情页URL',
          },
        },
        required: ['url'],
      },
    },
  ],
}));

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'search_jobs') {
      const { keyword, city, experience, page = 1 } = args;

      const browser = await puppeteer.launch({
        headless: 'new',
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--disable-gpu',
        ],
      });

      const browserPage = await browser.newPage();

      // 设置用户代理
      await browserPage.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      );

      // 设置视口
      await browserPage.setViewport({ width: 1920, height: 1080 });

      // 构建搜索URL
      let url = `https://www.zhipin.com/web/geek/job?query=${encodeURIComponent(
        keyword
      )}&city=${city}&page=${page}`;

      if (experience) {
        url += `&experience=${experience}`;
      }

      console.error(`正在访问: ${url}`);

      try {
        await browserPage.goto(url, {
          waitUntil: 'networkidle2',
          timeout: 30000,
        });

        // 等待职位卡片加载
        await browserPage.waitForSelector('.job-card-wrapper, .job-list-box', {
          timeout: 10000,
        });

        // 提取职位信息
        const jobs = await browserPage.evaluate(() => {
          const jobCards = document.querySelectorAll('.job-card-wrapper');

          return Array.from(jobCards).slice(0, 20).map((card) => {
            try {
              const jobName = card.querySelector('.job-name')?.textContent.trim() || '';
              const jobArea = card.querySelector('.job-area')?.textContent.trim() || '';
              const salary = card.querySelector('.salary')?.textContent.trim() || '';
              const companyName = card.querySelector('.company-name')?.textContent.trim() || '';
              const companyTag = Array.from(card.querySelectorAll('.company-tag-list li'))
                .map((li) => li.textContent.trim())
                .join(' / ');

              const tagList = Array.from(card.querySelectorAll('.tag-list li'))
                .map((li) => li.textContent.trim())
                .join(' / ');

              const infoDesc = card.querySelector('.info-desc')?.textContent.trim() || '';

              const link = card.querySelector('a.job-card-left');
              const jobUrl = link ? 'https://www.zhipin.com' + link.getAttribute('href') : '';

              return {
                date: new Date().toISOString().split('T')[0],
                company: companyName,
                companyInfo: companyTag,
                title: jobName,
                salary: salary,
                location: jobArea,
                tags: tagList,
                jd: infoDesc.substring(0, 200),
                url: jobUrl,
                matchScore: 0,
                matchReason: '',
                status: '新发现',
              };
            } catch (e) {
              console.error('提取职位信息出错:', e);
              return null;
            }
          }).filter(job => job !== null && job.company && job.title);
        });

        await browser.close();

        if (jobs.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(
                  {
                    success: false,
                    message: '未找到职位信息，可能需要登录或页面结构已变化',
                    jobs: [],
                  },
                  null,
                  2
                ),
              },
            ],
          };
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: true,
                  count: jobs.length,
                  keyword,
                  city,
                  page,
                  jobs,
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (error) {
        await browser.close();
        throw error;
      }
    } else if (name === 'get_job_detail') {
      const { url } = args;

      const browser = await puppeteer.launch({
        headless: 'new',
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
        ],
      });

      const browserPage = await browser.newPage();
      await browserPage.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      );

      try {
        await browserPage.goto(url, {
          waitUntil: 'networkidle2',
          timeout: 30000,
        });

        const detail = await browserPage.evaluate(() => {
          const jobName = document.querySelector('.job-name')?.textContent.trim();
          const salary = document.querySelector('.salary')?.textContent.trim();
          const jobDesc = document.querySelector('.job-sec-text')?.textContent.trim();
          const companyName = document.querySelector('.company-name')?.textContent.trim();

          return {
            jobName,
            salary,
            jobDesc,
            companyName,
          };
        });

        await browser.close();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(detail, null, 2),
            },
          ],
        };
      } catch (error) {
        await browser.close();
        throw error;
      }
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(
            {
              success: false,
              error: error.message,
              stack: error.stack,
            },
            null,
            2
          ),
        },
      ],
      isError: true,
    };
  }
});

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Boss直聘爬虫 MCP Server 已启动');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
