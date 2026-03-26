from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = 'dev'

# In-memory product catalog with categories, subcategories, images, and delivery
PRODUCTS = [
    # Patike - Yeezy
    {
        'id': 1,
        'name': 'Yeezy Boost 350 V2 (Cinder)',
        'price': 230,
        'category': 'Patike',
        'subcategory': 'Yeezy',
        'image': 'https://sneakernews.com/wp-content/uploads/2020/01/adidas-Yeezy-Boost-350-v2-Cinder-FY2903-0.jpg',
        'delivery': '2-4 days',
        'type': 'Muške',
        'season': 'Sve godine',
        'description': 'Premium Kanye West dizajn. Ultralagane i udobne sa Boost tehnologijom. Čekan model za kolekcionare i ljubitelje sneakera.',
    },
    {
        'id': 2,
        'name': 'Yeezy Boost 350 V2 (Static)',
        'price': 235,
        'category': 'Patike',
        'subcategory': 'Yeezy',
        'image': 'https://sneakerbardetroit.com/wp-content/uploads/2018/10/adidas-Yeezy-Boost-350-V2-Static-Reflective-EF2905-Release-Date-5.jpg',
        'delivery': '2-4 days',
        'type': 'Muške',
        'season': 'Sve godine',
        'description': 'Kultna verzija sa static obrascem. Moderna i udobna, idealno za svakodnevnu nošnju i događaje.',
    },
    # Patike - Jordan
    {
        'id': 3,
        'name': 'Jordan 1 Retro High OG (Chicago)',
        'price': 280,
        'category': 'Patike',
        'subcategory': 'Jordan',
        'image': 'https://cdn.shopify.com/s/files/1/1622/9929/products/Jordan1RetroHighOGChicagoLostandFoundMen_s1.png?v=1669453813',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Legedarna NBA patika. Ikoničan crveno-belo-crni dizajn. Savršena za basketball ili street style.',
    },
    {
        'id': 4,
        'name': 'Jordan 1 Retro High OG (Bred)',
        'price': 260,
        'category': 'Patike',
        'subcategory': 'Jordan',
        'image': 'https://sneakernews.com/wp-content/uploads/2018/01/air-jordan-1-bred-toe-555088-610-detailed-look-6.jpg?w=1140',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Klasična "Bred" verzija. Crven i crn detalj sa premium kožom. Investicija za svakog sneaker hedera.',
    },
    # Patike - Nike
    {
        'id': 5,
        'name': 'Nike Air Force 1 Low (White)',
        'price': 120,
        'category': 'Patike',
        'subcategory': 'Nike',
        'image': 'https://sneakerbardetroit.com/wp-content/uploads/2020/03/Nike-Air-Force-1-Low-Triple-White-315115-112-Release-Date-4.jpg',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Veikovni klasik. Čista bela boja, minimalističan dizajn. Savršena za bilo koji outfit, od casual do formal.',
    },
    {
        'id': 6,
        'name': 'Nike Air Max 90 (Crna)',
        'price': 130,
        'category': 'Patike',
        'subcategory': 'Nike',
        'image': 'https://picsum.photos/400/400?random=6',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Klasičan Air Max sa vidljiv Air jastuku. Odličan za proleće i jesen, udoban ceo dan.',
    },
    # Patike - Adidas
    {
        'id': 16,
        'name': 'Adidas Ultraboost 21 (Crna)',
        'price': 150,
        'category': 'Patike',
        'subcategory': 'Adidas',
        'image': 'https://static.ftshp.digital/img/p/1/1/0/0/9/2/6/1100926.jpg',
        'delivery': '2-4 days',
        'type': 'Women',
        'season': 'Sve godine',
        'description': 'Premium Boost tehnologija. Savršena za trčanje ili casual nošnju. Laganost i podrška su osigurani.',
    },
    {
        'id': 17,
        'name': 'Adidas Ultraboost 21 (Bela)',
        'price': 150,
        'category': 'Patike',
        'subcategory': 'Adidas',
        'image': 'https://cdn-images.farfetch-contents.com/19/67/44/19/19674419_43940203_1000.jpg',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Čista bela verzija za minimaliste. Elegantna za sve godišnje doba. Popularna kod fashion influensera.',
    },
    {
        'id': 18,
        'name': 'Nike React Vision (Black)',
        'price': 99,
        'category': 'Patike',
        'subcategory': 'Nike',
        'image': 'https://static.nike.com/a/images/t_PDP_1280_v1/f_auto,q_auto:eco/e674dc73-be5f-42c5-b991-2a128d699cf0/react-vision-shoe-dK1mnR.png',
        'delivery': '2-4 days',
        'type': 'Muške',
        'season': 'Leto/Proleće',
        'description': 'Neona žuta za letnje dane. Lagana React potplata. Idealno za fitness ili šetnje u toplije vreme.',
    },
    {
        'id': 19,
        'name': 'Jordan 4 (Siva)',
        'price': 200,
        'category': 'Patike',
        'subcategory': 'Jordan',
        'image': 'https://asset.snipes.com/images/f_auto,q_80,d_fallback-sni.png/b_rgb:f8f8f8,c_pad,w_680,h_680/dpr_1.0/02489454_6/jordan-jordan-4-retro-%22cave-stone%22-(gs)-siva-48362-6',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Retro Jordan 4 sa sivim tonom. Trapez detaljima i Jumpman logotipom. Ozbiljna kolekcionarska vrednost.',
    },
    # Patike - Nsport/Buzz/Djak
    {
        'id': 20,
        'name': 'Nsport',
        'price': "time",
        'category': 'Patike',
        'subcategory': 'Nsport',
        'image': 'data:image/webp;base64,UklGRjoPAABXRUJQVlA4IC4PAABwVQCdASqvAeoAPp1MokylpCMiIxG5mLATiU3cLhAf09f852tsp+xPzP5d/jB811mfv34i/JTn1Di9mn8D71Pmv/mf+v7MPMQ/VL9a+u95of2Z/aP3Xf99+0Xvc/uHqC/1P/mdbT6Cvlyfuh8RH7jeknqqH17+9d87+C2gm/HaJ9dNDXZfLFiFciZWLPJd+E5w7PP/Dx5Z5/4ePLPP/Dw/bKyvMYe6HV5jD3Q6vMW7OOzq8xh7odXmMPdDpvkH4Rph7odXmMPdDq3rkOrzGHuh2NkOxsh1b1KLqoiq2VCgDjEp4Y/a3pJmNkbWN2B4Mvn5REw9L0bQtUPGhvfqkeLwg1/NmbH9LZZOHPZcnZCnKjTSOBreP0Z0V6RZizEi73s5gaBFxEFsmG7QfiKrVrMRZEcGhpVSazVXn7URQUC7Yb252yybbLHE7xtZkOLTdYOh/OM1WcJLmUPLPtaG9EaRr9fc5bj494o69OyvJyRdtKOy9NazrmZLT2BecGTNvcomcn2Vjf2lpO6dFESCXktq5F4uLE4ZbSgFI3U7VYyKJAcA5v2QVtrTYLGL2b5ZgLCyMX7HNzuKRbuIEz2S45queWeGq6bnCJ8jNTdr/FVv3VdX3UeTgfJpkXeY4dwN/SyFxEgubTTali2YMhmBpH/f1HttJl637extK8RwdhFQ/KZqlsTDPJd5FbxH+8K2VMWw4demAtrrbwmxgtpS8zPsNNsIxPoO1RWNpv0WPPex2LXtXW5P+sqUbXaA4FYjac+sgpO7pnvadbWnw/blBV4SRM+nocioEA41K6y/4gDo+ZdcNg9iTPyuNRGcvAvttfUGmHuh1jmMEsASD8I0w90OrzGHuh1b1yHV5jD3Q6vMYe6HVvXIdXmMPdDq8xh7odW9gg8s8/8PHlnn/h48s8/8MGVgAAD+/AtCa/vQjRjeI/+yU6kl4BM1ore4QAfjg2D8gAAAAAAAARg+kdkAvd4GM/qkDDBK05GthsOh0cw9fx5X62caFcTiBFUCcgKwP/l0s782Jgm/KW6PE3IM2heedC2Vrmsr2iwx9jBGJy6c41R4z3mnoXjjwhmUudegItFAjLiy1/lvpAhg1DhMQCA1ociqpBgEdMlXcy2OAkLj/CisG8eFTbIIPUtQBS0ZOnbK26in1HN3PdzAnz6JACUVVBqu+TOF2JO2vAmbkk4c2yjw4kGt6kkuoVNikiCmS6gey3jZV5gvMl3dOGawrensXvHBEreBMXPTsOZjcOFMPeumHtO81kL7GR6sstSfIBN33eyG52QegXqJV0W2b+2d+s/Q3d7CvzqKvpyjJqFtL+81fQZca/QJrd4RYoBe8UQV39ff5jMEgYHblyQtIzcN2BqWpAravwMA+4OOX5nn/jd0DoBsLghRzx6Mvj0EeEeuV+6M0PUCQnIXVZQ/WEAeqyi63ojMNcps8D6T4ubkVas4nFV2wghd3S35XA65jW9GQ4EpXbBmLVOc+v1fivHGcS6P27fEJOVM8aUPUb1xXWoBWnlBk+xFkIUgc2Uc7TdeDCu/Wk5YM2KbiqXAXW9A4Y02nVA+uDnN6XOyri2vxZZBvDzftQqVbLdBBsT+/kwEg3lWRzw6TxdZjpxTgItPJRG1+VKImAC2XleJ/gn9Q8CLkz9NoA5+FUOqtHkUlaXdEkhvjgzwdu1MJ6DJiYMWppFMQtiOXNWOlVHLcIIUoSDqIp1DA9SVyiNzQbRk3OrHPOalCmrqXAtF4rSRIsV8Gy3653mEoyXGQTnsWIGETu/l/Q5Ri6mReQAld9aMhwnxBSMUho1XInNfHX2Tcul91mv3QEXjaXPE4IgEWLuoj6aSVboDXtnTmyO8irctLOZhWYy9I0Q9urLDhA84gsYP5ungTORa3m18ib8ovK9YKfrCl57ipPtQR5EbkdGiiX0ol/+QY1l2zLStx/0szczaR6uR7uCuCx8zQyPkv3eA+qJrx2Zk2Vve0vbkvXVC1kcVwSiUsU6s+5NTodrXfrg/xohKWwDcoJgMOxHPFqBcN9lN3NBrXCybrNoBcN6evw4ADxcuz6vA8dwCU7FtoTNHwwRkMmONCwyOwEdaUkCfrm9N74qtjmCDyD9+u10eWSnQeA+vQFrOWBp+UvStNBbX15WkhSoR0FNxtQVqOcsjAPeiZ3kM7fTihfNZ7GoGiyNuQXMb1SOo1Z9mrSXS1KEbjkggVm4FWDOWmmBHF6dCFAgzldnVwZFq7O9IjeQc078Eqjz9YB5H+d+hSe8xOkS0VcbxIiUUh+zzF5o93CJLm/Q0dN6EnJCVquR7iJOWujNHc4KCytAWSNrw2IAEF+5f/6QHukpVIgDPjKGaap9dBVnX+qW7rtA9sQ2Zje8dp1/XE36qSI8QrzhbDuVKV9mGpmLeFBCTsJ4O/ATj7zCjkHb3AAtpS1fpMt3u9R6CNMMpwmAHMaMS0hRlJFR2sWwiJKcXlgppRWVaMhQPXtIGlMZTB5TKcCwxVV0mBQ1EAbp0zNDM+zZu1gR/sffhWZ/ujM4HGAV25yV7yEd9lgh988tntezn7ZWNZPlznAHO57kJcDp9RSjc540pHJkyzluQIthxXCdRJ0+V8tuRX0s7v3pgv02dUgsSB2hYCan+Goisiix76eboMM491WQH87TiidowWp2uYPEHpyGIlZWFfhpoD3TZdTVGbMK9EmdhOnzVM1zvF+YLYL80VgiI9vNOzLfQEyTZ2iHZWMjeskRe+KGH6f68nmqjGO8uCX27dJ18F0hXwsWx2NtyxKdbglTjmODfqq85k0rLnN3yZAagDe5CzOxJXFgAlINM/mSx6cY3Ee4ul7TOoOxZGFCTT1kVayLE2KopZnaUDUamjvu4eo1MKA7NEBiUfqOpBlbvuXLN/FubupZQnvHVQjN06i8Ts12uYmfmOn+EiRjM25/5n+X61j2xqWzrqJEX8PToQkR2EC+B/IIamvn4n+PGNUctlMsVL4+HvlAekajsVjgMC6Zprhxs0zG5mSIOzcydEEWEJsqiFd0YMVoVxhVohBOaX0sFZ1qPmvlAdbfQKgGgzGeJPLTo/OL7s2wPM9mfYksC3ZDwy2x/r32DncWshDM9PbnHV57OmKRNv7Df5mp5DaEC2pTpv1rtzwtrtzq8z9oGd2g1NqjPMfU/hMzY7S/UlI7mbnwK352dl1jieD0nm4yin5H3uuBtS4AM1L438WdR2jjsYuqZt+ZZ5NgQjB1vEj5kEPd9muNQIFoeLN3LZmwrlRTqNTDTfR1DzH0ioceTWECVAUYYVyAw4ejMFiEO5XqpUNELpKG7XT7ps/RXqAGhh5/afLXWMUR+AN1ImFO+I0TuAA/+byx8GLJpMxpekKIcZG+f/VINIS7kYHr3Iat5g5mX3SI6fQjSa7/eRO+8oymBSG+XRI3Wx0ESXW6er3pWoXhHgwBp1fsMiXsDzuEzIaldvp0pBOzS23YSd8CmnVtTtPaEJ+SH2SPFNBBIK5HN+P+1lI1DQ/9CKicYjPFVEwXBgI1Lk+o7gkIEX9OZuge+Ogmdiho6g4cPU8I0DRcU2CXlwSl09wUUDZVpfJI/7raVKGl/+iKYefVeH1cZkrwLov3pkqGAj2YP1CdsAVDGlb7ROtn9b8rnDmxqVGWjrOqrMplevuuo1LXXaCAE1DAJYTsm/dMiPMal+RtTraauXJkSTP6j4AwB/yZeYlPyw2gvG/kf05JkSaurEdUCDX71HS6kmPFmyGrsbSClMT+SwVGSOb2j5QIZO5xKhV3r92wbkVsMsbWYtpAdv6EREqNmbG/n+JJUHEFr7y/Wa9jwbX51Z0EM3B2ycrKFUGTe5jZpEY+abV7MNpTdHeHrXikTXGdVoypjj5lkop3qQz+1i+IgaGkm/BuWSODfzwn3tjIcTXGOl5OwrrDJ5L60/1Y36eby4RVtPP2agZBzS2mn0t0XVEFKIE/Rk+La0vOmPwTRrE5YTNeveQv6jvW+3x3X/OF0POlW/Edt/uWgwWiNrFSbbMy/ujPFf2ItZivCj5khAHUEDryyTiNMTfyEvZzE5S3WO3yA/iQ1xCW093vuoFFMkTIrexo49JpGBp0wtA9woQprNWABkOhDii3JYlRbxWaDLhuCAi+MAsER4yOX/EOkmkASyCu6ucdMWTg2iL2GS257uIPBkWjFC3g1Rsuirot9VHUKsi8OTPGqXkKrJy+qa1oPuVgHC+K/UWTIx2Q0rVhlE41+NhgHJzJYHvpI2b3+D8GC6uGtjnk7KhNxpOF6T1QQ387S17xYS4SbeWCZGetSD6w+ibNEQIaRJCQckB+gRcP6zDX+3aSsZfvf7Qol5WoU7AlW2vBzY9NHe14k08tXOjgyqOylOCnfjGTm9g0TZsU/oH69aqfUzInMsCCwooZJqUdYwLXXl6cTRNx3stxznvC8Iyroiesr0abr2EREWj73Yl/gJ9xPnilaTzZ07TfLnAaKDiLnLhCG06ZTbvsKyjSI+hBadWfUqpMlOTFflyUyPAS3eOW1/oaC/xR++O6c7gq/D8tfAkhAJArhkcwvXUrBH0P+iwB4N3a4/YInGbfTgGMzKmScqGgEbtY1OS2dr4YVo0hwA89wE30e4kwKpVec1crbDdtRWr17lbncKcVhp7Wip4ZZxoYDVNxHJOvsAk26b8/DAVGGJclnQBx7AzU0jJaC8ok7esr+pzjyL57LBPpEo9XC99o4a/y5E6GVNgNWr0vzUW2ZW/qfaH3gIBfGnIOKR7FICUm9yvi6VaoYaiGy106t1vJ6tp/V0ZPXKaQD8F8Z/5BJiSPDHbdfCCggklSKhouEh2Jk/kxXrPGwsjg+cRh5afJHaYafeR5NAckHs3xXRfPTilrerKc3ibkfAbyVyFcMW7pmhQcEV1nUjHhgavDQVf0VWMbQ4Zi1wmSQt0kKabkjs+9sAyHii6bR5G7FLhfS+pEA10v5FBEt1yLTQgmtXLH6QiSKDs3/5/A+pQ1RFe4LZ/6eOELsM409hSdr4h2E48aHFEVWB+lc1DfhxGj+w67WX/NRjKQiyOjNFI6qmYtzFNgg7DceZRSOku7cY7o7ZbgqFRCJ2kUC7mJlUVZEnS0AsqGjVF2CC77Q73/pGl1EY81Ii+RymYB3JrO+crZfXgKQt9ckGfjBC/Vo9//ACWLyBsz4AAGTsAAAAAAAAAAAEuxh+ABXpK76S8AA',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'good company go and check them out too',
    },
    {
        'id': 21,
        'name': 'Buzz',
        'price': 105,
        'category': 'Patike',
        'subcategory': 'Buzz',
        'image': '',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'good street wear company go and check them out too',
    },
    {
        'id': 22,
        'name': 'Djak',
        'price': 95,
        'category': 'Patike',
        'subcategory': 'Djak',
        'image': 'https://picsum.photos/400/400?random=13',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'good company go check them out, especially if you are a fan of Nikola Jokić',
    },
    # Odeća - Majice
    {
        'id': 7,
        'name': 'Inat majica GM (Bela)',
        'price': 25,
        'category': 'Odeća',
        'subcategory': 'Majice',
        'image': 'https://yt3.googleusercontent.com/f5SlZln56A8c_UYTqt0mDWISIdCTIceDBll5MMpiDRrUFPL0xJVNw31oLNXXpqR2vaM1FnbTpZw=s900-c-k-c0x00ffffff-no-rj',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Bela majica sa prepoznatljivim starim srbskim inat logom GM. Kvalitetan pamuk, udobna i moderna. Savršena za svakodnevnu nošnju i ljubitelje brenda.',
    },
    {
        'id': 8,
        'name': 'Grafička majica (Bela)',
        'price': 17,
        'category': 'Odeća',
        'subcategory': 'Majice',
        'image': 'https://picsum.photos/400/400?random=15',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Minimalni dizajn na beloj majici. Kombinuje se sa sve. Osnovni komad garderobe.',
    },
    # Odeća - Dukserice
    {
        'id': 9,
        'name': 'Dukserica (Siva)',
        'price': 40,
        'category': 'Odeća',
        'subcategory': 'Dukserice',
        'image': 'https://picsum.photos/400/400?random=16',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Jesen/Zima',
        'description': 'Topla i udobna siva dukserica. Savršena za hladnije dane. Džepovi sa zatvaračem.',
    },
    {
        'id': 12,
        'name': 'Dukserica (Crna)',
        'price': 40,
        'category': 'Odeća',
        'subcategory': 'Dukserice',
        'image': 'https://picsum.photos/400/400?random=17',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Jesen/Zima',
        'description': 'Klasična crna dukserica za svaki outfit. Debela i izdržljiva. Odličnog kvaliteta.',
    },
    # Odeća - Pantalone
    {
        'id': 13,
        'name': 'Pantalone (Plave)',
        'price': 35,
        'category': 'Odeća',
        'subcategory': 'Pantalone',
        'image': 'https://picsum.photos/400/400?random=18',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Moderne plave pantalone sa fleksibilnim pamуkom. Udobne za ceo dan. Moderne boje.',
    },
    {
        'id': 14,
        'name': 'Šorcevi (Crni)',
        'price': 30,
        'category': 'Odeća',
        'subcategory': 'Šorcevi',
        'image': 'https://picsum.photos/400/400?random=19',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Leto',
        'description': 'Lagani letnji šorcevi sa elastičnom pojasom. Odlični za plažu i sport. Brzo se suše.',
    },
    # Nakit - Ogrlice
    {
        'id': 10,
        'name': 'Srebrna ogrlica',
        'price': 60,
        'category': 'Nakit',
        'subcategory': 'Ogrlice',
        'image': 'https://picsum.photos/400/400?random=20',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Elegantna srebrna ogrlica sa minimalnim dizejalnom. Savršena za svečane prilike.',
    },
    {
        'id': 15,
        'name': 'Narukvica (Koža)',
        'price': 45,
        'category': 'Nakit',
        'subcategory': 'Narukvice',
        'image': 'https://picsum.photos/400/400?random=21',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Ručno savijena pravoj kože narukvica. Dugovečna i udobna. Poveća se vremenom.',
    },
    {
        'id': 11,
        'name': 'Zlatni prsten',
        'price': 90,
        'category': 'Nakit',
        'subcategory': 'Prstenovi',
        'image': 'https://picsum.photos/400/400?random=22',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Premium zlatni prsten sa sitnim detaljima. Komad koji vrijednosti raste. Savršen poklon.',
    },
]

# Mock vendor API endpoint (would be actual URLs in real app)
VENDOR_API_URL = 'https://example-vendor.com/api/order'

@app.route('/')
def index():
    # category and subcategory filters
    category = request.args.get('category')
    subcat = request.args.get('subcategory')

    filtered = PRODUCTS
    if category:
        filtered = [p for p in filtered if p['category'] == category]
    if subcat:
        filtered = [p for p in filtered if p.get('subcategory') == subcat]

    # build category->subcategories mapping
    categories = {}
    for p in PRODUCTS:
        cat = p['category']
        sub = p.get('subcategory') or 'All'
        categories.setdefault(cat, set()).add(sub)
    # sort subcategories and convert to list
    categories = {cat: sorted(subs) for cat, subs in categories.items()}

    return render_template(
        'index.html',
        products=filtered,
        categories=categories,
        selected_category=category,
        selected_subcategory=subcat,
    )

@app.route('/order/<int:product_id>', methods=['GET', 'POST'])
def order(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        flash('Product not found')
        return redirect(url_for('index'))
    if request.method == 'POST':
        customer = {
            'name': request.form['name'],
            'address': request.form['address'],
            'phone': request.form['phone'],
        }
        # Here we would process payment; skipping for now
        # Simulate vendor order
        success = place_vendor_order(product, customer)
        if success:
            flash('Order placed successfully!')
            return redirect(url_for('index'))
        else:
            flash('Vendor order failed.')
            return redirect(url_for('order', product_id=product_id))
    return render_template('order.html', product=product)


def place_vendor_order(product, customer):
    # In a real implementation we would POST to vendor API with auth and data.
    # Here we just print to console and pretend it succeeded.
    print(f"Placing vendor order for {product['name']} to {customer}")
    # Example of what you might do with requests:
    # resp = requests.post(VENDOR_API_URL, json={
    #     'product_id': product['id'],
    #     'quantity': 1,
    #     'delivery': customer
    # })
    # return resp.status_code == 200
    return True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
