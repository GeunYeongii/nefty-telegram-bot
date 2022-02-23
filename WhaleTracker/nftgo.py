from cmath import isnan
import requests, json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from currency_converter import CurrencyConverter
from .utils import func_args_preprocessing

class nftgoAPI :
    __API_URL_BASE = 'https://api.nftgo.io/api/v1/'
    data = []
    coll = []
    
    def get_json(self):
        return self.jsonfile
    def get_data(self):
        return self.data
    def gete_coll(self):
        return self.coll

    def __init__(self, api_base_url=__API_URL_BASE):
        self.api_base_url = api_base_url
        self.request_timeout = 120

        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        
    def __request(self, url):
        # print(url)
        try:
            response = self.session.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise

        try:
            response.raise_for_status()
            content = json.loads(response.content.decode('utf-8'))
            if isinstance(content,dict):
                self.jsonfile = content
            return content
        except Exception as e:
            # check if json (with error message) is returned
            try:
                content = json.loads(response.content.decode('utf-8'))
                raise ValueError(content)
            # if no json
            except json.decoder.JSONDecodeError:
                pass

            raise

    def __api_url_params(self, api_url, params, api_url_has_params=False):
        if params:
            # if api_url contains already params and there is already a '?' avoid
            # adding second '?' (api_url += '&' if '?' in api_url else '?'); causes
            # issues with request parametes (usually for endpoints with required
            # arguments passed as parameters)
            api_url += '&' if api_url_has_params else '?'
            for key, value in params.items():
                if type(value) == bool:
                    value = str(value).lower()

                api_url += "{0}={1}&".format(key, value)
            api_url = api_url[:-1]
        return api_url
    
    # ---------- PING ----------#
    def ping(self):
        """Check API server status"""

        api_url = '{0}ping'.format(self.api_base_url)
        return self.__request(api_url)


    
    # ---------- Whales Bought NFT List ----------#
    @func_args_preprocessing
    def get_bought_list(self, hour=1, action="buy",acs=1,by="Price", **kwargs):
        """
            고래들의 구매 리스트 순위
        __default__
        hour=1          (1시간 기준),
        action='buy'    (구매 정보만 보기),  
        acs=1           (오름차순(내림차순은 acs=0)),  
        by='Price'      (가격기준으로 오름차순),  

        Returns:  
            _type_: _None_  
        """
        kwargs['timeRank'] = str(hour) + 'h'
        kwargs['action'] = action.replace(' ', '')
        kwargs['acs'] = acs
        kwargs['by'] = by.replace(' ', '')

        api_url = '{0}whales/data/list/topSales'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)
        
        self.jsonfile = self.__request(api_url)
        for data in self.jsonfile["data"] :
            self.data.append(data)
            self.coll.append(data['coll'])
    
    @func_args_preprocessing
    def get_price_list(self,*args,**kwargs):
        """__고래들이 구매한 nft 가격 리스트__
            
        nft.get_price_list([넣고싶은 환율])
        
        __example__
        nft.get_price_list('USD','ETH') -> USD와 ETH 리스트만 추출

        Returns:  
            _type_: _dict in list_  
        """
        c = CurrencyConverter()
        price_list = []
        
        for nft in self.data :
            
            if 'USD' in args :
                kwargs['USD'] = round(nft['price'],3),'USD'
            if 'KRW' in args :
                kwr = c.convert(nft['price'],'USD','KRW')
                kwargs['KRW'] = round(kwr,3),'KRW'
            if 'ETH' in args :
                kwargs['ETH'] = round(nft['tokenPrice'],3),nft['payToken']['symbol']
            
            price_list.append(kwargs)
            kwargs = {}
        
        return price_list        
    
    @func_args_preprocessing
    def get_change_list(self,args=[],**kwargs) :
        """__가격 변s동률(변동 가격, 퍼센트) 리스트__

        __example__
        nft.get_change_list()
        >> [{'price: 1875.42', 'percent':62.62'......}]
        
        Returns:
            __type__: __dict in list__
        """
        
        for nft in self.data :
            kwargs['price'] =  format(nft['changePrice'],'.2f') if (nft['changePrice']) else 0
            kwargs['percent'] = format(nft['changePercent']*100,'.2f') if (nft['changePrice']) else 0
            kwargs['ETH'] = format(nft['tokenPriceChange'],'.4f') if (nft['tokenPriceChange']) else 0
            args.append(kwargs)
            kwargs = {}
        
        return args  
        
    @func_args_preprocessing    
    def get_buyer_list(self,args=[],**kwargs) :
        """__고래 구매자 주소 리스트__

        __example__
        nft.get_buyer_list()
        >> ['0x1243','0x5678'......]
        
        Returns:
            __type__: __list__
        """
        for nft in self.data :

        
            args.append(nft['buyer'])
            
        return args
    
    @func_args_preprocessing
    def get_name_list(self,args=[],**kwargs) :
        """__구매 NFT 이름 리스트__

        __example__
        nft.get_name_list()
        >> ['Mutant Ape Yacht Club #4689'......]
        
        Returns:
            __type__: __list__
        """
        for nft in self.data :
            args.append(nft['nft']['name'])
            
        return args
    
    @func_args_preprocessing
    def get_nft_image(self,args=[],**kwargs) :
        """__고래가 구매한 nft 이미지 리스트__
        
        Returns:
            __type__: __list__
        """
        for nft in self.data :
            if len(nft['nft']['image']) > 100 :
                args.append(None)
            else :
                args.append(nft['nft']['image'])
            
        return args
    
    # ---------- Whales Bought Collection List ----------#

    @func_args_preprocessing
    def get_coll_Name(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 이름 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['name'])
        return args

    @func_args_preprocessing
    def get_coll_pageLink(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 링크 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['link'])
        return args
    
    @func_args_preprocessing
    def get_coll_openseaLink(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 Opensea 링크 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['openseaLink'])
        return args

    @func_args_preprocessing
    def get_coll_logo(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 로고 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['logo'])
        return args
    
    @func_args_preprocessing
    def get_coll_twitter(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 트위터 링크 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['twitter'])
        return args
    
    @func_args_preprocessing
    def get_coll_discord(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 디스코드 링크 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['discord'])
        return args
    
    @func_args_preprocessing
    def get_coll_youtube(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 유튜브 링크 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['youtube'])
        return args

    @func_args_preprocessing
    def get_coll_instagram(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 인스타그램 링크 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['instagram'])
        return args
    
    @func_args_preprocessing
    def get_coll_contractUrls(self,args=[],**kwargs) :
        """__고래가 구매한 NFT의 컬랙션 컨트랙트 링크 리스트__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['contractUrls'][0])
        return args
    




