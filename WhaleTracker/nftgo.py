from cmath import isnan
import requests, json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from currency_converter import CurrencyConverter
from .utils import func_args_preprocessing
from datetime import datetime

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
            ???????????? ?????? ????????? ??????
        __default__
        hour=1          (1?????? ??????),
        action='buy'    (?????? ????????? ??????),  
        acs=1           (????????????(??????????????? acs=0)),  
        by='Price'      (?????????????????? ????????????),  

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
        """__???????????? ????????? nft ?????? ?????????__
            
        nft.get_price_list([???????????? ??????])
        
        __example__
        nft.get_price_list('USD','ETH') -> USD??? ETH ???????????? ??????

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
        """__?????? ???s??????(?????? ??????, ?????????) ?????????__

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
        """__?????? ????????? ?????? ?????????__

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
        """__?????? NFT ?????? ?????????__

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
        """__????????? ????????? nft ????????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for nft in self.data :
            if len(nft['nft']['image']) > 100 :
                args.append(None)
            else :
                args.append(nft['nft']['image'])
            
        return args
    
    def get_nft_time(self,args=[],**kwargs) :
        """__????????? nft??? ????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for nft in self.data :
            time = nft['time']/1000
            minute = str(datetime.now()-datetime.fromtimestamp(time))
                   
            if int(minute[:1]) >= 1 :
                args.append('1??????')
            else :
                args.append(minute[2:4]+'???')    
            
        return args
    # ---------- Whales Bought Collection List ----------#

    @func_args_preprocessing
    def get_coll_Name(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['name'])
        return args

    @func_args_preprocessing
    def get_coll_pageLink(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['link'])
        return args
    
    @func_args_preprocessing
    def get_coll_openseaLink(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? Opensea ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['openseaLink'])
        return args

    @func_args_preprocessing
    def get_coll_logo(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['logo'])
        return args
    
    @func_args_preprocessing
    def get_coll_twitter(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['twitter'])
        return args
    
    @func_args_preprocessing
    def get_coll_discord(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ???????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['discord'])
        return args
    
    @func_args_preprocessing
    def get_coll_youtube(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['youtube'])
        return args

    @func_args_preprocessing
    def get_coll_instagram(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ??????????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['medias']['instagram'])
        return args
    
    @func_args_preprocessing
    def get_coll_contractUrls(self,args=[],**kwargs) :
        """__????????? ????????? NFT??? ????????? ???????????? ?????? ?????????__
        
        Returns:
            __type__: __list__
        """
        for collection in self.coll :
            args.append(collection['contractUrls'][0])
        return args
    




