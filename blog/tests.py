from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

class Testview(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_naruto = User.objects.create_user(username='naruto', password='somepassword')
        self.user_itachi = User.objects.create_user(username='itachi', password='somepassword')

        self.user_itachi.is_staff = True
        self.user_itachi.save()

        self.category_growing = Category.objects.create(name='성장과정', slug='성장과정')
        self.category_mode = Category.objects.create(name='모드변화', slug='모드변화')

        self.tag_ama = Tag.objects.create(name='아마테라스', slug='아마테라스')
        self.tag_uchiha = Tag.objects.create(name='uchiha', slug='uchiha')
        self.tag_hello= Tag.objects.create(name='hello', slug='hello')


        self.post_001 = Post.objects.create(
            title='첫번째 포스트입니다.',
            content='우즈마키 나루토',
            category=self.category_growing,
            author=self.user_naruto
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두번째 포스트입니다.',
            content='우치하 이타치',
            category=self.category_mode,
            author=self.user_itachi
        )

        self.post_003 = Post.objects.create(
            title='세번째 포스트입니다.',
            content='카테고리가 없을 수도 있죠',
            author=self.user_itachi
        )
        self.post_003.tags.add(self.tag_uchiha)
        self.post_003.tags.add(self.tag_ama)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        logo_btn = navbar.find('a', text = '나루토 키우기!')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_mode.name} ({self.category_mode.post_set.count()})',
                      categories_card.text)
        self.assertIn(f'{self.category_growing.name} ({self.category_growing.post_set.count()})',
                      categories_card.text)
        self.assertIn(f'미분류 ({Post.objects.filter(category=None).count()})', categories_card.text)

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니닷떼바용', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_ama.name, post_001_card.text)
        self.assertNotIn(self.tag_uchiha.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_ama.name, post_002_card.text)
        self.assertNotIn(self.tag_uchiha.name, post_002_card.text)


        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_ama.name, post_003_card.text)
        self.assertIn(self.tag_uchiha.name, post_003_card.text)

        self.assertIn(self.user_naruto.username.upper(), main_area.text)
        self.assertIn(self.user_itachi.username.upper(), main_area.text)

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니닷떼바용', main_area.text)

    def test_post_detail(self):
            self.assertEqual(self.post_001.get_absolute_url(),'/blog/1/')

            response = self.client.get(self.post_001.get_absolute_url())
            self.assertEqual(response.status_code, 200)

            soup = BeautifulSoup(response.content, 'html.parser')

            self.navbar_test(soup)
            self.category_card_test(soup)

            self.assertIn(self.post_001.title, soup.title.text)

            main_area = soup.find('div', id='main-area')
            post_area = main_area.find('div', id='post-area')
            self.assertIn(self.post_001.title, post_area.text)
            self.assertIn(self.category_growing.name, post_area.text)

            self.assertIn(self.user_naruto.username.upper(), post_area.text)
            self.assertIn(self.post_001.content, post_area.text)

            self.assertIn(self.tag_hello.name, post_area.text)
            self.assertNotIn(self.tag_ama.name, post_area.text)
            self.assertNotIn(self.tag_uchiha.name, post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_growing.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_growing.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_growing.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_growing.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='naruto', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='itachi', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
                         {
                             'title':'Post Form 만들기',
                             'content':'Post Form 페이지를 만듭시다.',
                             'tags_str': 'new tag; 한글 태그, hello'
                         }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, 'Post Form 만들기')
        self.assertEqual(last_post.author.username, 'itachi')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        self.assertNotEqual(self.post_003.author, self.user_naruto)
        self.client.login(
            username = self.user_naruto.username,
            password = 'somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        self.client.login(
            username = self.post_003.author.username,
            password = 'somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)
        
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('아마테라스; uchiha', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
             {
                 'title':'세번째 포스트를 수정했습니다.',
                 'content':'그림자 분신술!',
                 'category':self.category_mode.pk,
                 'tags_str':'풍둔;대옥,나선환'
             },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('그림자 분신술!', main_area.text)
        self.assertIn(self.category_mode.name, main_area.text)
        self.assertIn('풍둔', main_area.text)
        self.assertIn('대옥', main_area.text)
        self.assertIn('나선환', main_area.text)
        self.assertNotIn('uchiha', main_area.text)






