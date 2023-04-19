import time
import logging
import requests
import json
import os

from aiogram import Bot, Dispatcher, executor, types
from selenium import webdriver
from selenium.webdriver.common.by import By
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN_TG_BOT')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

text = """
Тестовый текст
для многострочного сообщения
ага, а вот здесь {} имя пользователя

а тут твое сообщение:
{}
"""


class Form(StatesGroup):
    choice = State()  # Will be represented in storage as 'Form:name'


table_data_list = ['1', 'Bitcoin', 'BTC', '$27,682.79', '0.02% 1.50% 13.15%', '$534,986,861,920', '$31,561,686,051', '1,140,227 BTC', '19,325,612 BTC', '2', 'Ethereum', 'ETH', '$1,755.39', '0.03% 1.86% 6.70%', '$214,813,667,416', '$12,507,247,361', '7,127,965 ETH', '122,373,866 ETH', '3', 'Tether', 'USDT', '$1.00', '0.02% 0.05% 0.02%', '$77,610,900,445', '$48,446,343,073', '48,341,218,256 USDT', '77,436,340,550 USDT', '4', 'BNB', 'BNB', '$326.00', '0.37% 2.54% 2.87%', '$51,466,261,332', '$1,092,587,099', '3,358,081 BNB', '157,890,352 BNB', '5', 'USD Coin', 'USDC', '$0.9991', '0.02% 0.02% 0.02%', '$34,693,518,688', '$6,436,376,188', '6,441,458,294 USDC', '34,719,676,175 USDC', '6', 'XRP', 'XRP', '$0.4439', '1.81% 1.08% 22.52%', '$22,617,144,356', '$2,991,349,133', '6,757,311,922 XRP', '50,950,912,949 XRP', '7', 'Cardano', 'ADA', '$0.3737', '0.32% 0.75% 15.37%', '$12,975,859,918', '$626,026,813', '1,677,777,665 ADA', '34,719,132,875 ADA', '8', 'Dogecoin', 'DOGE', '$0.07648', '1.63% 1.37% 9.13%', '$10,146,859,485', '$668,721,122', '8,879,433,646 DOGE', '132,670,764,300 DOGE', '9', 'Polygon', 'MATIC', '$1.12', '0.23% 1.32% 0.18%', '$9,812,173,469', '$546,884,738', '486,883,221 MATIC', '8,734,317,475 MATIC', '10', 'Solana', 'SOL', '$21.71', '0.21% 2.33% 12.13%', '$8,333,571,580', '$839,231,108', '38,642,699 SOL', '383,779,634 SOL', '11', 'Binance USD', 'BUSD', '$0.9998', '0.03% 0.05% 0.01%', '$8,062,062,828', '$5,450,276,714', '5,451,601,604 BUSD', '8,064,021,527 BUSD', '12', 'Polkadot', 'DOT', '$6.20', '0.02% 1.11% 3.61%', '$7,245,530,316', '$237,696,772', '38,347,682 DOT', '1,169,213,520 DOT', '13', 'Litecoin', 'LTC', '$88.74', '0.95% 9.82% 13.22%', '$6,437,318,848', '$1,149,356,214', '12,995,826 LTC', '72,543,277 LTC', '14', 'Shiba Inu', 'SHIB', '$0.00001074', '0.28% 0.84% 3.61%', '$6,332,304,807', '$310,182,377', '28,957,110,152,168 SHIB', '589,543,917,125,050 SHIB', '15', 'TRON', 'TRX', '$0.06207', '0.06% 7.39% 5.77%', '$5,657,011,496', '$805,805,729', '12,971,661,052 TRX', '91,143,363,370 TRX', '16', 'Avalanche', 'AVAX', '$17.29', '0.56% 0.57% 10.68%', '$5,630,203,045', '$311,991,073', '18,044,949 AVAX', '325,654,623 AVAX', '17', 'Dai', 'DAI', '$0.9989', '0.02% 0.10% 0.07%', '$5,487,031,026', '$267,556,556', '267,792,104 DAI', '5,492,110,775 DAI', '18', 'Uniswap', 'UNI', '$6.18', '0.02% 2.72% 4.96%', '$4,708,242,152', '$100,767,560', '16,317,430 UNI', '762,209,327 UNI', '19', 'Wrapped Bitcoin', 'WBTC', '$27,676.83', '0.04% 1.48% 13.16%', '$4,158,621,947', '$330,221,352', '11,931 WBTC', '150,251 WBTC', '20', 'Chainlink', 'LINK', '$7.42', '1.49% 0.16% 12.79%', '$3,834,750,797', '$515,074,620', '69,581,582 LINK', '517,099,970 LINK', '21', 'Cosmos', 'ATOM', '$11.64', '0.29% 0.78% 6.53%', '$3,333,721,486', '$193,981,713', '16,660,948 ATOM', '286,370,297 ATOM', '22', 'UNUS SED LEO', 'LEO', '$3.35', '0.40% 0.67% 0.01%', '$3,192,895,381', '$891,127', '266,035 LEO', '953,954,130 LEO', '23', 'Ethereum Classic', 'ETC', '$20.68', '0.15% 1.34% 11.94%', '$2,896,055,833', '$238,368,966', '11,545,018 ETC', '140,042,609 ETC', '24', 'Toncoin', 'TON', '$2.32', '0.15% 3.52% 4.96%', '$2,837,862,074', '$32,495,969', '14,013,918 TON', '1,221,401,181 TON', '25', 'Monero', 'XMR', '$153.18', '0.10% 1.18% 3.97%', '$2,796,626,029', '$135,640,766', '886,710 XMR', '18,256,062 XMR', '26', 'OKB', 'OKB', '$45.34', '0.31% 0.80% 2.50%', '$2,719,690,612', '$37,142,902', '819,614 OKB', '60,000,000 OKB', '27', 'Stellar', 'XLM', '$0.09343', '0.37% 0.14% 10.85%', '$2,481,888,922', '$129,176,299', '1,382,761,605 XLM', '26,561,321,746 XLM', '28', 'Bitcoin Cash', 'BCH', '$128.12', '0.08% 3.35% 2.70%', '$2,478,522,388', '$211,888,534', '1,654,724 BCH', '19,344,381 BCH', '29', 'Filecoin', 'FIL', '$5.75', '0.52% 0.32% 0.10%', '$2,355,496,709', '$368,462,544', '64,093,898 FIL', '409,345,443 FIL', '30', 'Aptos', 'APT', '$12.66', '0.24% 5.34% 4.19%', '$2,244,080,325', '$559,054,571', '44,171,808 APT', '177,305,846 APT', '31', 'TrueUSD', 'TUSD', '$0.9991', '0.04% 0.02% 0.05%', '$2,039,798,764', '$270,628,305', '270,884,809 TUSD', '2,041,445,064 TUSD', '32', 'Lido DAO', 'LDO', '$2.36', '0.00% 0.35% 0.03%', '$2,023,840,330', '$174,505,070', '73,906,695 LDO', '857,926,340 LDO', '33', 'Hedera', 'HBAR', '$0.06142', '0.16% 2.33% 2.65%', '$1,852,895,821', '$49,141,879', '800,878,972 HBAR', '30,162,396,684 HBAR', '34', 'Cronos', 'CRO', '$0.06939', '0.06% 2.22% 0.03%', '$1,752,953,062', '$16,625,139', '240,025,768 CRO', '25,263,013,692 CRO', '35', 'NEAR Protocol', 'NEAR', '$1.99', '0.21% 1.12% 2.85%', '$1,724,831,077', '$131,813,158', '66,252,404 NEAR', '866,021,029 NEAR', '36', 'VeChain', 'VET', '$0.02324', '0.07% 0.20% 4.95%', '$1,685,571,828', '$75,249,264', '3,233,384,111 VET', '72,511,146,418 VET', '37', 'Stacks', 'STX', '$1.16', '0.16% 4.77% 29.79%', '$1,580,575,849', '$533,071,102', '459,703,996 STX', '1,367,476,957 STX', '38', 'Algorand', 'ALGO', '$0.2182', '0.28% 7.63% 5.64%', '$1,555,429,445', '$163,272,311', '748,880,007 ALGO', '7,128,876,442 ALGO', '39', 'Quant', 'QNT', '$126.21', '0.11% 2.38% 1.94%', '$1,523,805,806', '$27,443,758', '217,523 QNT', '12,072,738 QNT', '40', 'Internet Computer', 'ICP', '$5.09', '0.08% 2.01% 1.61%', '$1,517,526,412', '$47,745,229', '9,400,692 ICP', '298,002,646 ICP', '41', 'ApeCoin', 'APE', '$4.08', '0.32% 0.32% 1.71%', '$1,502,007,086', '$139,685,004', '34,227,210 APE', '368,593,750 APE', '42', 'The Graph', 'GRT', '$0.1538', '0.67% 3.54% 3.73%', '$1,366,337,111', '$123,868,150', '803,842,203 GRT', '8,882,752,870 GRT', '43', 'Fantom', 'FTM', '$0.4886', '0.10% 3.18% 22.96%', '$1,359,652,077', '$499,890,211', '1,023,146,597 FTM', '2,782,907,223 FTM', '44', 'EOS', 'EOS', '$1.14', '0.73% 1.65% 7.86%', '$1,233,130,589', '$199,785,330', '176,244,712 EOS', '1,086,122,784 EOS', '45', 'BitDAO', 'BIT', '$0.5322', '0.08% 3.30% 0.78%', '$1,112,630,342', '$14,443,118', '27,128,934 BIT', '2,090,946,169 BIT', '46', 'Decentraland', 'MANA', '$0.5996', '0.30% 0.89% 7.40%', '$1,112,285,488', '$122,726,054', '204,610,613 MANA', '1,855,084,192 MANA', '47', 'Aave', 'AAVE', '$77.12', '0.28% 1.00% 4.31%', '$1,087,078,725', '$77,237,361', '1,001,481 AAVE', '14,093,193 AAVE', '48', 'MultiversX', 'EGLD', '$42.79', '0.19% 1.96% 4.24%', '$1,077,087,179', '$37,424,742', '874,929 EGLD', '25,168,647 EGLD', '49', 'Tezos', 'XTZ', '$1.15', '0.79% 1.63% 3.35%', '$1,070,032,105', '$32,399,855', '28,289,602 XTZ', '931,601,714 XTZ', '50', 'Immutable', 'IMX', '$1.22', '0.03% 1.21% 1.63%', '$1,057,422,521', '$121,018,940', '99,285,726 IMX', '868,583,515 IMX', '51', 'Flow', 'FLOW', '$1.01', '0.12% 2.95% 3.83%', '$1,047,525,372', '$54,527,220', '53,894,877 FLOW', '1,036,200,000 FLOW', '52', 'Theta Network', 'THETA', '$1.02', '0.08% 0.12% 0.81%', '$1,022,494,431', '$30,169,872', '29,477,017 THETA', '1,000,000,000 THETA', '53', 'Conflux', 'CFX', '$0.3833', '0.45% 4.85% 37.62%', '$1,018,254,238', '$619,594,342', '1,618,378,742 CFX', '2,656,581,495 CFX', '54', 'Axie Infinity', 'AXS', '$8.52', '0.42% 0.82% 8.32%', '$985,196,624', '$63,699,683', '7,469,506 AXS', '115,605,573 AXS', '55', 'The Sandbox', 'SAND', '$0.648', '0.14% 0.86% 10.16%', '$971,636,587', '$183,932,147', '283,922,595 SAND', '1,499,470,108 SAND', '56', 'KuCoin Token', 'KCS', '$9.04', '0.07% 2.51% 2.14%', '$889,317,121', '$2,187,761', '242,278 KCS', '98,379,861 KCS', '57', 'Pax Dollar', 'USDP', '$0.9983', '0.03% 0.11% 0.04%', '$877,588,179', '$6,711,864', '6,713,611 USDP', '878,084,065 USDP', '58', 'Neo', 'NEO', '$12.18', '0.64% 1.91% 15.48%', '$859,184,633', '$85,604,672', '7,013,403 NEO', '70,538,831 NEO', '59', 'Chiliz', 'CHZ', '$0.1217', '0.48% 0.13% 5.66%', '$817,773,550', '$83,634,606', '687,176,597 CHZ', '6,718,673,350 CHZ', '60', 'Optimism', 'OP', '$2.53', '0.11% 2.08% 4.86%', '$795,556,933', '$239,202,728', '94,447,685 OP', '314,844,141 OP', '61', 'Rocket Pool', 'RPL', '$38.82', '0.50% 3.13% 2.08%', '$747,657,020', '$8,433,210', '217,108 RPL', '19,257,026 RPL', '62', 'Terra Classic', 'LUNC', '$0.0001261', '0.25% 1.25% 1.55%', '$744,682,776', '$67,504,515', '536,133,131,289 LUNC', '5,906,591,532,234 LUNC', '63', 'USDD', 'USDD', '$0.9925', '0.03% 0.06% 0.02%', '$719,914,484', '$35,443,322', '35,711,558 USDD', '725,332,036 USDD', '64', 'Curve DAO Token', 'CRV', '$0.9585', '0.50% 2.64% 5.90%', '$717,629,935', '$82,831,510', '86,425,318 CRV', '748,726,670 CRV', '65', 'Mina', 'MINA', '$0.8174', '0.29% 0.90% 2.31%', '$712,917,876', '$62,018,912', '75,722,630 MINA', '872,126,275 MINA', '66', 'Klaytn', 'KLAY', '$0.2286', '0.13% 1.74% 2.77%', '$703,813,114', '$39,190,575', '171,614,872 KLAY', '3,079,436,405 KLAY', '67', 'Bitcoin SV', 'BSV', '$36.39', '0.14% 4.38% 4.79%', '$701,081,209', '$51,133,945', '1,406,812 BSV', '19,266,077 BSV', '68', 'Synthetix', 'SNX', '$2.72', '0.26% 2.28% 4.47%', '$689,035,426', '$83,172,578', '30,584,422 SNX', '253,638,040 SNX', '69', 'PancakeSwap', 'CAKE', '$3.76', '0.08% 1.65% 1.66%', '$686,420,648', '$45,652,813', '12,160,201 CAKE', '182,798,895 CAKE', '70', 'Maker', 'MKR', '$682.61', '0.12% 0.95% 7.86%', '$667,336,064', '$62,773,275', '91,844 MKR', '977,631 MKR', '71', 'GMX', 'GMX', '$77.22', '0.33% 3.93% 4.61%', '$661,500,159', '$80,273,749', '1,039,087 GMX', '8,566,564 GMX', '72', 'Dash', 'DASH', '$57.87', '0.22% 1.01% 10.09%', '$648,003,434', '$130,289,131', '2,257,634 DASH', '11,195,792 DASH', '73', 'Gemini Dollar', 'GUSD', '$1.01', '0.15% 0.06% 1.77%', '$610,927,547', '$968,673', '962,382 GUSD', '607,049,883 GUSD', '74', 'SingularityNET', 'AGIX', '$0.5023', '0.78% 3.43% 5.02%', '$605,863,233', '$313,876,447', '624,662,870 AGIX', '1,206,121,857 AGIX', '75', 'eCash', 'XEC', '$0.00003088', '0.02% 1.01% 3.14%', '$597,183,580', '$9,416,736', '305,082,631,951 XEC', '19,340,298,423,303 XEC', '76', 'Frax Share', 'FXS', '$7.99', '0.09% 3.58% 1.65%', '$595,431,324', '$39,297,922', '4,913,251 FXS', '74,551,029 FXS', '77', 'Huobi Token', 'HT', '$3.65', '0.15% 9.20% 9.95%', '$591,998,121', '$20,588,240', '5,639,875 HT', '162,233,844 HT', '78', 'IOTA', 'MIOTA', '$0.2115', '0.24% 1.99% 3.65%', '$587,764,663', '$13,793,498', '65,253,047 MIOTA', '2,779,530,283 MIOTA', '79', 'BitTorrent(New)', 'BTT', '$0.0000006166', '0.14% 1.48% 5.83%', '$587,045,107', '$18,893,623', '30,611,374,151,828 BTT', '951,421,714,286,000 BTT', '80', 'Zcash', 'ZEC', '$35.03', '0.37% 2.16% 5.29%', '$571,965,186', '$36,749,571', '1,048,843 ZEC', '16,328,269 ZEC', '81', 'GateToken', 'GT', '$5.24', '0.56% 0.50% 2.66%', '$567,321,087', '$1,544,506', '294,684 GT', '108,265,077 GT', '82', 'XDC Network', 'XDC', '$0.03921', '0.11% 3.61% 25.54%', '$542,093,449', '$5,896,091', '150,381,254 XDC', '13,823,681,988 XDC', '83', 'PAX Gold', 'PAXG', '$1,979.93', '0.14% 1.62% 2.74%', '$537,086,770', '$20,582,460', '10,399 PAXG', '271,264 PAXG', '84', 'Trust Wallet Token', 'TWT', '$1.20', '0.27% 0.28% 0.15%', '$499,780,735', '$22,991,310', '19,151,425 TWT', '416,649,900 TWT', '85', 'Render Token', 'RNDR', '$1.35', '0.15% 0.69% 7.00%', '$489,558,735', '$123,451,506', '91,302,944 RNDR', '361,444,954 RNDR', '86', 'Loopring', 'LRC', '$0.3447', '0.11% 1.05% 10.03%', '$458,498,672', '$56,040,077', '162,729,114 LRC', '1,330,133,546 LRC', '87', 'THORChain', 'RUNE', '$1.39', '0.25% 2.37% 3.66%', '$456,166,414', '$52,336,745', '37,529,746 RUNE', '327,056,566 RUNE', '88', 'Zilliqa', 'ZIL', '$0.02784', '0.43% 1.24% 4.31%', '$441,691,332', '$36,735,408', '1,321,218,001 ZIL', '15,867,699,447 ZIL', '89', '1inch Network', '1INCH', '$0.5095', '0.22% 3.33% 3.66%', '$425,202,574', '$30,614,919', '60,224,897 1INCH', '834,559,362 1INCH', '90', 'Fei USD', 'FEI', '$0.9713', '0.03% 0.30% 2.27%', '$412,785,325', '$752,812', '767,961 FEI', '424,996,178 FEI', '91', 'Mask Network', 'MASK', '$5.33', '0.77% 5.26% 36.72%', '$405,764,147', '$211,955,773', '39,824,034 MASK', '76,150,000 MASK', '92', 'Convex Finance', 'CVX', '$5.35', '0.07% 3.51% 0.15%', '$404,696,228', '$8,667,881', '1,620,544 CVX', '75,650,397 CVX', '93', 'Kava', 'KAVA', '$0.8822', '0.44% 4.96% 18.85%', '$398,757,652', '$29,891,444', '33,818,202 KAVA', '452,006,537 KAVA', '94', 'Osmosis', 'OSMO', '$0.8076', '0.19% 1.53% 5.36%', '$397,837,329', '$9,328,402', '11,542,075 OSMO', '492,590,761 OSMO', '95', 'Casper', 'CSPR', '$0.03663', '0.20% 2.17% 3.11%', '$397,186,188', '$8,723,512', '237,657,435 CSPR', '10,843,869,994 CSPR', '96', 'Enjin Coin', 'ENJ', '$0.398', '0.18% 0.14% 3.15%', '$397,997,573', '$32,733,926', '82,273,051 ENJ', '1,000,000,000 ENJ', '97', 'dYdX', 'DYDX', '$2.50', '0.10% 0.76% 6.88%', '$391,049,164', '$181,909,056', '72,624,500 DYDX', '156,256,174 DYDX', '98', 'Nexo', 'NEXO', '$0.696', '0.35% 2.69% 12.37%', '$389,734,421', '$5,280,299', '7,576,910 NEXO', '560,000,011 NEXO', '99', 'Flare', 'FLR', '$0.03166', '1.15% 2.20% 9.37%', '$379,952,555', '$57,450,118', '1,814,459,183 FLR', '11,999,991,148 FLR', '100', 'MAGIC', 'MAGIC', '$1.75', '0.53% 2.68% 4.37%', '$371,679,915', '$309,928,683', '177,458,156 MAGIC', '212,495,238 MAGIC']
dict = []

def get_info():
    browser = webdriver.Chrome()
    browser.get("https://coinmarketcap.com/")
    for i in range(8):
        browser.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)

    block = browser.find_element(By.TAG_NAME, 'tbody')
    table_data_list = block.text.split("\n")
    update_info()

def update_info():
    banned_indeces = [4, 6, 7, 8]
    banned = []

    for ind in banned_indeces:
        banned += [i for i in range(ind, len(table_data_list), 9)]

    newMassiv = [data for data in table_data_list if table_data_list.index(
        data) not in banned]
    for i in range(0, len(newMassiv), 5):
        dict.append({})

    for j, i in zip(range(100), range(0, len(newMassiv), 5)):
        dict[j]['id'] = newMassiv[i]
        dict[j]['coin'] = {}
        dict[j]['coin']['NAME'] = newMassiv[i + 1]
        dict[j]['coin']['SYMBOL'] = newMassiv[i + 2]
        dict[j]['coin']['PRICE'] = newMassiv[i + 3]
        dict[j]['coin']['MARKET_CAP'] = newMassiv[i + 4]


def function(number_of_coins):

    number_of_coins = int(number_of_coins)
    newDict = []
    for i in range(number_of_coins):
        newDict.append(dict[i])
    return json.dumps(newDict, indent=4)

    # with open("E:\code\SelParse\SPJ.json", "w", encoding="utf-8") as file:
    #     json.dump(dict, file, indent=4, ensure_ascii=False)
    # print("Script succesfully complete!")


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} {user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    # await message.reply(f'Privet, {user_full_name}') - ответ на сообщение
    # for i in range(1):
    # time.sleep(2)
    await bot.send_message(user_id, text.format(message.from_user.username, message.text))  # прислать сообщение


@dp.message_handler(commands=['ftjgvnyhfhcjtgvytgyhjfrtgyhrffjtgyhrtghfyrtghfyj'])
async def get_zapros(message: types.Message):
    myacc_csgo = requests.get("https://steamcommunity.com/inventory/76561198259026080/730/2?l=russian&count=1000")
    dict = json.loads(myacc_csgo.text)
    logging.info(f'wants steam {time.asctime()} {message.from_user.username}')
    otvet = f"""
    {myacc_csgo}

    {dict}
    """
    await bot.send_message(message.from_user.id, otvet)


@dp.message_handler(commands=['bot_ip'])
async def get_ip(message: types.Message):
    my_ip = requests.get("http://api.myip.com")
    logging.info(f'wants ip {time.asctime()} {message.from_user.username}')
    await bot.send_message(message.from_user.id, json.loads(my_ip.text))


@dp.message_handler(commands=['market'])
async def get_crypto(message: types.Message):
    logging.info(f'wants get crypto data {time.asctime()} {message.from_user.username}')

    await Form.choice.set()
    await message.reply(f'{message.from_user.username}, сколько криптовалют хочешь получить?\n(цифра от 1 до 100)')


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='back')
@dp.message_handler(Text(equals='back', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.')


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.choice)
async def process_age_invalid(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Необходимо ввести цифру от 1 до 100.")


@dp.message_handler(lambda message: int(message.text) not in [i for i in range(1, 101)], state=Form.choice)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Необходимо выбрать цифру от 1 до 100")


@dp.message_handler(lambda message: message.text.isdigit() and (int(message.text) in [i for i in range(1, 101)]),
                    state=Form.choice)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(choice=int(message.text))
    string = function(message.text)
    async with state.proxy() as data:
        data['choice'] = message.text
        await bot.send_message(message.chat.id, string)
    # Finish conversation
    await state.finish()


if __name__ == '__main__':
    print('bebra')
    update_info()
    executor.start_polling(dp)
